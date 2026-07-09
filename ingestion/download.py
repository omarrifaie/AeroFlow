"""Download the raw OpenFlights ``.dat`` files into ``data/raw/``.

The download is idempotent: a dataset that is already present on disk is skipped
unless ``force=True`` is passed. This keeps repeated pipeline runs (and CI) fast
and avoids hammering the upstream host.
"""

from __future__ import annotations

from pathlib import Path

import requests

from ingestion.sources import DATASETS, Dataset

# Repository root is two levels up from this file (``ingestion/download.py``).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Generous but bounded timeout so a hung connection fails fast in CI.
_REQUEST_TIMEOUT_SECONDS = 60


def download_dataset(dataset: Dataset, raw_dir: Path = RAW_DIR, force: bool = False) -> Path:
    """Download a single dataset to ``raw_dir`` and return the local file path.

    Args:
        dataset: The dataset to download.
        raw_dir: Destination directory (created if missing).
        force: Re-download even when the file already exists.

    Returns:
        Path to the downloaded file on disk.
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    destination = raw_dir / dataset.filename

    if destination.exists() and not force:
        print(f"[download] {dataset.name}: cached ({destination.relative_to(PROJECT_ROOT)})")
        return destination

    print(f"[download] {dataset.name}: fetching {dataset.url}")
    response = requests.get(dataset.url, timeout=_REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    # Write bytes to preserve the file exactly as served; encoding is handled at
    # load time. Latin-1/UTF-8 mix in OpenFlights is dealt with in load.py.
    destination.write_bytes(response.content)
    kib = len(response.content) / 1024
    print(
        f"[download] {dataset.name}: wrote {kib:,.1f} KiB -> {destination.relative_to(PROJECT_ROOT)}"
    )
    return destination


def download_all(raw_dir: Path = RAW_DIR, force: bool = False) -> list[Path]:
    """Download every configured dataset. Returns the list of local paths."""
    return [download_dataset(dataset, raw_dir=raw_dir, force=force) for dataset in DATASETS]


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    download_all()
