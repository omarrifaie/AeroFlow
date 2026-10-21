"""Download the raw OpenFlights ``.dat`` files into ``data/raw/``.

The download is idempotent: a dataset that is already present on disk is skipped
unless ``force=True`` is passed. This keeps repeated pipeline runs (and CI) fast
and avoids hammering the upstream host.
"""

from __future__ import annotations

from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ingestion.sources import DATASETS, Dataset

# Repository root is two levels up from this file (``ingestion/download.py``).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Generous but bounded timeout so a hung connection fails fast in CI.
_REQUEST_TIMEOUT_SECONDS = 60

# Retry transient failures (dropped connections, 429 and 5xx) with exponential
# backoff so a brief upstream hiccup does not fail the whole pipeline.
_RETRY_POLICY = Retry(
    total=3,
    backoff_factor=1.0,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET",),
)


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
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=_RETRY_POLICY))
        response = session.get(dataset.url, timeout=_REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    # Write bytes to preserve the file exactly as served; load.py decodes them as
    # UTF-8. Writing to a sibling file and renaming means an interrupted download
    # never leaves a truncated file behind that later runs would treat as cached.
    partial = destination.with_name(f"{destination.name}.part")
    partial.write_bytes(response.content)
    partial.replace(destination)
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
