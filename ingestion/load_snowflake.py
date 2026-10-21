"""Load the raw OpenFlights files from ``data/raw/`` into Snowflake.

The Snowflake counterpart of :mod:`ingestion.load_databricks`, used by the
``snowflake`` dbt target. Each file is parsed by the exact same DuckDB
``read_csv`` call as the local loader, written to Parquet, uploaded to an
internal stage, and then materialised as an all-``VARCHAR`` table in the ``RAW``
schema with a ``_loaded_at`` timestamp. Snowflake's CSV file format is not used,
so empty strings, ``NULL`` and quoting come out identical on every target.

Connection details come from the same environment variables, with the same
defaults, that the ``snowflake`` target in ``transform/profiles.yml`` reads (see
``.env.example``). The database must already exist; the ``RAW`` schema, the stage
and the tables are created when missing. Identifiers are left unquoted so
Snowflake upper-cases them, exactly as it does for dbt's unquoted source names.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import duckdb
import snowflake.connector
from snowflake.connector.cursor import SnowflakeCursor

from ingestion.download import RAW_DIR
from ingestion.load import RAW_SCHEMA, export_parquet
from ingestion.sources import DATASETS, Dataset

# Internal named stage (inside the raw schema) that holds the uploaded Parquet files.
LANDING_STAGE = "landing"
_REQUIRED_ENV_VARS = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD")
# Same fallbacks as the snowflake target in transform/profiles.yml.
_OPTIONAL_ENV_VARS = {
    "SNOWFLAKE_ROLE": "TRANSFORMER",
    "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
    "SNOWFLAKE_DATABASE": "AEROFLOW",
}


def _connection_settings() -> dict[str, str]:
    """Read the Snowflake connection settings from the environment."""
    missing = [name for name in _REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            f"Missing environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env, fill in the Snowflake values and export them."
        )
    settings = {name: os.environ[name] for name in _REQUIRED_ENV_VARS}
    for name, default in _OPTIONAL_ENV_VARS.items():
        settings[name] = os.environ.get(name) or default
    return settings


def load_dataset(
    cursor: SnowflakeCursor,
    local: duckdb.DuckDBPyConnection,
    dataset: Dataset,
    database: str,
    staging_dir: Path,
    raw_dir: Path = RAW_DIR,
) -> int:
    """Load one dataset into ``<database>.RAW.<raw_table>`` and return the row count."""
    parquet_path = export_parquet(local, dataset, staging_dir, raw_dir=raw_dir)

    stage = f"@{database}.{RAW_SCHEMA}.{LANDING_STAGE}"
    # Streamed upload: the file:// path only names the staged file.
    with parquet_path.open("rb") as stream:
        cursor.execute(
            f"PUT 'file://{parquet_path.name}' {stage} AUTO_COMPRESS = FALSE OVERWRITE = TRUE",
            file_stream=stream,
        )

    table = f"{database}.{RAW_SCHEMA}.{dataset.raw_table}"
    # Parquet rows arrive as one VARIANT ($1); casting a field to VARCHAR yields SQL
    # NULL for Parquet nulls and keeps empty strings as they are.
    columns = ", ".join(f'$1:"{name}"::VARCHAR AS {name}' for name in dataset.columns)
    cursor.execute(
        f"CREATE OR REPLACE TABLE {table} AS "
        f"SELECT {columns}, CURRENT_TIMESTAMP() AS _loaded_at "
        f"FROM {stage}/{parquet_path.name}"
    )
    cursor.execute(f"SELECT count(*) FROM {table}")
    (row_count,) = cursor.fetchone()
    print(f"[load] {database}.{RAW_SCHEMA}.{dataset.raw_table}: {row_count:,} rows")
    return row_count


def load_all_snowflake(raw_dir: Path = RAW_DIR) -> dict[str, int]:
    """Load every dataset into Snowflake. Returns a mapping of table name -> rows."""
    settings = _connection_settings()
    database = settings["SNOWFLAKE_DATABASE"]
    counts: dict[str, int] = {}
    with (
        tempfile.TemporaryDirectory(prefix="aeroflow-") as staging_dir,
        duckdb.connect() as local,
        snowflake.connector.connect(
            account=settings["SNOWFLAKE_ACCOUNT"],
            user=settings["SNOWFLAKE_USER"],
            password=settings["SNOWFLAKE_PASSWORD"],
            role=settings["SNOWFLAKE_ROLE"],
            warehouse=settings["SNOWFLAKE_WAREHOUSE"],
            database=database,
        ) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{RAW_SCHEMA}")
        cursor.execute(
            f"CREATE STAGE IF NOT EXISTS {database}.{RAW_SCHEMA}.{LANDING_STAGE} "
            "FILE_FORMAT = (TYPE = PARQUET)"
        )
        for dataset in DATASETS:
            counts[dataset.raw_table] = load_dataset(
                cursor, local, dataset, database, Path(staging_dir), raw_dir=raw_dir
            )
    print(f"[load] Snowflake raw schema ready at {database}.{RAW_SCHEMA}")
    return counts


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    load_all_snowflake()
