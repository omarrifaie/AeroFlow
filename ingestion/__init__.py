"""AeroFlow ingestion package.

Downloads the raw OpenFlights static data files and loads them into the ``raw``
schema of the local DuckDB warehouse (``load``), Snowflake (``load_snowflake``)
or Databricks (``load_databricks``). Kept deliberately small and free of
side effects at import time so it can be driven from the pipeline CLI.
"""
