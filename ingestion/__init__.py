"""AeroFlow ingestion package.

Downloads the raw OpenFlights static data files and loads them into a local
DuckDB warehouse under the ``raw`` schema. Kept deliberately small and free of
side effects at import time so it can be driven from the pipeline CLI.
"""
