"""AeroFlow pipeline CLI.

A small `typer` app that orchestrates the end-to-end flow:

    ingest      download raw OpenFlights files -> data/raw/
    load        load raw files -> DuckDB (schema `raw`)
    transform   run `dbt deps` + `dbt build` (models and tests)
    all         run ingest -> load -> transform in order

Run it as a module:

    python -m pipeline.cli all
    python -m pipeline.cli ingest --force
    python -m pipeline.cli transform --target duckdb
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import typer

from ingestion.download import download_all
from ingestion.load import load_all

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = PROJECT_ROOT / "transform"

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="AeroFlow: ingest OpenFlights data, load DuckDB, and build dbt models.",
)


def _run_dbt(command: list[str], target: str) -> None:
    """Invoke dbt as a subprocess against the transform/ project.

    dbt is called through ``python -m dbt.cli.main`` so it always resolves to the
    interpreter running this CLI (i.e. the project's virtualenv), regardless of
    whether a ``dbt`` executable is on PATH.
    """
    full_command = [
        sys.executable,
        "-m",
        "dbt.cli.main",
        *command,
        "--project-dir",
        str(DBT_PROJECT_DIR),
        "--profiles-dir",
        str(DBT_PROJECT_DIR),
        "--target",
        target,
    ]
    printable = " ".join(command)
    typer.echo(f"[transform] dbt {printable} (target={target})")
    result = subprocess.run(full_command, cwd=str(DBT_PROJECT_DIR), check=False)
    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)


@app.command()
def ingest(
    force: bool = typer.Option(False, "--force", help="Re-download even if cached."),
) -> None:
    """Download the raw OpenFlights ``.dat`` files into ``data/raw/``."""
    download_all(force=force)


@app.command()
def load() -> None:
    """Load the raw files into the DuckDB ``raw`` schema."""
    load_all()


@app.command()
def transform(
    target: str = typer.Option("duckdb", "--target", "-t", help="dbt target to build."),
) -> None:
    """Run ``dbt deps`` then ``dbt build`` (models and tests)."""
    _run_dbt(["deps"], target=target)
    _run_dbt(["build"], target=target)


@app.command()
def all(
    force: bool = typer.Option(False, "--force", help="Re-download even if cached."),
    target: str = typer.Option("duckdb", "--target", "-t", help="dbt target to build."),
) -> None:
    """Run the whole pipeline: ingest -> load -> transform."""
    download_all(force=force)
    load_all()
    _run_dbt(["deps"], target=target)
    _run_dbt(["build"], target=target)
    typer.echo("[all] pipeline complete.")


if __name__ == "__main__":
    app()
