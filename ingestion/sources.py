"""Definitions of the raw OpenFlights datasets ingested by AeroFlow.

Each :class:`Dataset` captures everything the download and load steps need:
the logical name, the upstream URL, the ordered column names (the OpenFlights
``.dat`` files ship *without* a header row), and the target raw table name.

Data source: OpenFlights (https://openflights.org/data.html), distributed under
the Open Database License (ODbL). See the project README for attribution.
"""

from __future__ import annotations

from dataclasses import dataclass

# The OpenFlights ``.dat`` files are comma-separated, have no header row, and
# use the literal two-character string ``\N`` to represent SQL NULL.
NULL_TOKEN = r"\N"

_BASE_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data"


@dataclass(frozen=True)
class Dataset:
    """A single raw OpenFlights dataset.

    Attributes:
        name: Logical dataset name (``airports``, ``airlines``, ``routes``).
        url: Upstream URL of the raw ``.dat`` file.
        columns: Ordered column names, matching the file's column order.
        raw_table: Destination table name inside the DuckDB ``raw`` schema.
    """

    name: str
    url: str
    columns: tuple[str, ...]
    raw_table: str

    @property
    def filename(self) -> str:
        """Local filename used when the dataset is downloaded to ``data/raw/``."""
        return f"{self.name}.dat"


DATASETS: tuple[Dataset, ...] = (
    Dataset(
        name="airports",
        url=f"{_BASE_URL}/airports.dat",
        columns=(
            "airport_id",
            "name",
            "city",
            "country",
            "iata",
            "icao",
            "latitude",
            "longitude",
            "altitude",
            "timezone",
            "dst",
            "tz_database_time_zone",
            "type",
            "source",
        ),
        raw_table="raw_airports",
    ),
    Dataset(
        name="airlines",
        url=f"{_BASE_URL}/airlines.dat",
        columns=(
            "airline_id",
            "name",
            "alias",
            "iata",
            "icao",
            "callsign",
            "country",
            "active",
        ),
        raw_table="raw_airlines",
    ),
    Dataset(
        name="routes",
        url=f"{_BASE_URL}/routes.dat",
        columns=(
            "airline",
            "airline_id",
            "source_airport",
            "source_airport_id",
            "destination_airport",
            "destination_airport_id",
            "codeshare",
            "stops",
            "equipment",
        ),
        raw_table="raw_routes",
    ),
)


def get_dataset(name: str) -> Dataset:
    """Return the :class:`Dataset` with the given ``name`` or raise ``KeyError``."""
    for dataset in DATASETS:
        if dataset.name == name:
            return dataset
    valid = ", ".join(d.name for d in DATASETS)
    raise KeyError(f"Unknown dataset '{name}'. Valid names: {valid}")
