"""Load the raw OpenFlights files from ``data/raw/`` into DuckDB.

Each dataset is loaded into the ``raw`` schema of ``transform/aeroflow.duckdb``
as an all-``VARCHAR`` table (types are cast later in the dbt staging layer, which
keeps ingestion dumb and makes bad values debuggable in SQL). The literal token
``\\N`` used by OpenFlights is converted to SQL ``NULL`` at read time, and a
``_loaded_at`` timestamp is attached to every table so dbt source-freshness has a
column to watch.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from ingestion.download import PROJECT_ROOT, RAW_DIR
from ingestion.sources import DATASETS, NULL_TOKEN, Dataset

DUCKDB_PATH = PROJECT_ROOT / "transform" / "aeroflow.duckdb"
RAW_SCHEMA = "raw"


def _read_csv_expression(dataset: Dataset, file_path: Path) -> str:
    """Build a DuckDB ``read_csv`` SELECT that yields all-VARCHAR raw columns.

    All columns are read as ``VARCHAR`` so ingestion never fails on a stray value;
    casting and validation happen in the dbt staging models instead.
    """
    columns_struct = ", ".join(f"'{name}': 'VARCHAR'" for name in dataset.columns)
    # ``nullstr`` matches the whole (unquoted) field value; ``\N`` -> NULL.
    # Forward slashes work on every platform, including Windows.
    return f"""
        SELECT
            *,
            current_timestamp AS _loaded_at
        FROM read_csv(
            '{file_path.as_posix()}',
            header = false,
            columns = {{ {columns_struct} }},
            nullstr = '{NULL_TOKEN}',
            quote = '"',
            escape = '"',
            encoding = 'utf-8',
            ignore_errors = false
        )
    """


def load_dataset(con: duckdb.DuckDBPyConnection, dataset: Dataset, raw_dir: Path = RAW_DIR) -> int:
    """Load one dataset into ``raw.<raw_table>`` and return the row count."""
    file_path = raw_dir / dataset.filename
    if not file_path.exists():
        raise FileNotFoundError(
            f"Raw file for '{dataset.name}' not found at {file_path}. "
            "Run the ingest step first (e.g. `python -m pipeline.cli ingest`)."
        )

    select_sql = _read_csv_expression(dataset, file_path)
    con.execute(f"CREATE OR REPLACE TABLE {RAW_SCHEMA}.{dataset.raw_table} AS {select_sql}")
    (row_count,) = con.execute(f"SELECT count(*) FROM {RAW_SCHEMA}.{dataset.raw_table}").fetchone()
    print(f"[load] {dataset.raw_table}: {row_count:,} rows")
    return row_count


def load_all(duckdb_path: Path = DUCKDB_PATH, raw_dir: Path = RAW_DIR) -> dict[str, int]:
    """Load every dataset into DuckDB. Returns a mapping of table name -> rows."""
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    con = duckdb.connect(str(duckdb_path))
    try:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")
        for dataset in DATASETS:
            counts[dataset.raw_table] = load_dataset(con, dataset, raw_dir=raw_dir)
    finally:
        con.close()
    print(f"[load] warehouse ready at {duckdb_path.relative_to(PROJECT_ROOT)}")
    return counts


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    load_all()
