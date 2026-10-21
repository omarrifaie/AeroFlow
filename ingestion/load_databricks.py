"""Load the raw OpenFlights files from ``data/raw/`` into Databricks.

The Databricks counterpart of :mod:`ingestion.load`, used by the ``databricks``
dbt target. Each file is parsed by the exact same DuckDB ``read_csv`` call as the
local loader, written to Parquet, uploaded to a Unity Catalog volume, and then
materialised as an all-``STRING`` table in the ``raw`` schema with a
``_loaded_at`` timestamp. Spark's CSV reader is deliberately not used: it turns
unquoted empty fields into ``NULL`` where DuckDB keeps an empty string, which
would make the raw layer (and every model built on it) differ between targets.

Connection details come from the same environment variables that the
``databricks`` target in ``transform/profiles.yml`` reads (see ``.env.example``).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import duckdb
from databricks import sql
from databricks.sql.client import Cursor

from ingestion.download import RAW_DIR
from ingestion.load import RAW_SCHEMA, export_parquet
from ingestion.sources import DATASETS, Dataset

# Managed volume (inside the raw schema) that holds the uploaded Parquet files.
LANDING_VOLUME = "landing"
DEFAULT_CATALOG = "workspace"
_REQUIRED_ENV_VARS = ("DATABRICKS_HOST", "DATABRICKS_HTTP_PATH", "DATABRICKS_TOKEN")


def _connection_settings() -> dict[str, str]:
    """Read the Databricks connection settings from the environment."""
    missing = [name for name in _REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            f"Missing environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env, fill in the Databricks values and export them."
        )
    return {name: os.environ[name] for name in _REQUIRED_ENV_VARS}


def load_dataset(
    cursor: Cursor,
    local: duckdb.DuckDBPyConnection,
    dataset: Dataset,
    catalog: str,
    staging_dir: Path,
    raw_dir: Path = RAW_DIR,
) -> int:
    """Load one dataset into ``<catalog>.raw.<raw_table>`` and return the row count."""
    parquet_path = export_parquet(local, dataset, staging_dir, raw_dir=raw_dir)

    volume_path = f"/Volumes/{catalog}/{RAW_SCHEMA}/{LANDING_VOLUME}/{parquet_path.name}"
    with parquet_path.open("rb") as stream:
        cursor.execute(
            f"PUT '__input_stream__' INTO '{volume_path}' OVERWRITE", input_stream=stream
        )

    table = f"`{catalog}`.`{RAW_SCHEMA}`.`{dataset.raw_table}`"
    columns = ", ".join(f"`{name}`" for name in dataset.columns)
    cursor.execute(
        f"CREATE OR REPLACE TABLE {table} AS "
        f"SELECT {columns}, current_timestamp() AS _loaded_at "
        f"FROM read_files('{volume_path}', format => 'parquet')"
    )
    cursor.execute(f"SELECT count(*) FROM {table}")
    (row_count,) = cursor.fetchone()
    print(f"[load] {catalog}.{RAW_SCHEMA}.{dataset.raw_table}: {row_count:,} rows")
    return row_count


def load_all_databricks(raw_dir: Path = RAW_DIR) -> dict[str, int]:
    """Load every dataset into Databricks. Returns a mapping of table name -> rows."""
    settings = _connection_settings()
    catalog = os.environ.get("DATABRICKS_CATALOG") or DEFAULT_CATALOG
    counts: dict[str, int] = {}
    with (
        tempfile.TemporaryDirectory(prefix="aeroflow-") as staging_dir,
        duckdb.connect() as local,
        sql.connect(
            server_hostname=settings["DATABRICKS_HOST"],
            http_path=settings["DATABRICKS_HTTP_PATH"],
            access_token=settings["DATABRICKS_TOKEN"],
        ) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{RAW_SCHEMA}`")
        cursor.execute(f"CREATE VOLUME IF NOT EXISTS `{catalog}`.`{RAW_SCHEMA}`.`{LANDING_VOLUME}`")
        for dataset in DATASETS:
            counts[dataset.raw_table] = load_dataset(
                cursor, local, dataset, catalog, Path(staging_dir), raw_dir=raw_dir
            )
    print(f"[load] Databricks raw schema ready at {catalog}.{RAW_SCHEMA}")
    return counts


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    load_all_databricks()
