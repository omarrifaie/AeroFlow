# AeroFlow Architecture

AeroFlow is a linear ELT pipeline: **extract** the raw OpenFlights files,
**load** them untouched into the warehouse (DuckDB by default, or Snowflake or
Databricks), then **transform** them in dbt through three
increasingly refined layers before serving them to an Evidence dashboard. Each
arrow below is a one-way dependency; nothing downstream writes back upstream.

```mermaid
flowchart TD
    OF["OpenFlights .dat files<br/>(airports · airlines · routes)"]

    subgraph ingest["1 · Ingestion (Python)"]
        DL["download.py<br/>idempotent fetch → data/raw/"]
        LD["load.py / load_snowflake.py / load_databricks.py<br/>read_csv · \\N → NULL · all VARCHAR<br/>+ _loaded_at"]
    end

    subgraph raw["2 · Raw (schema: raw)"]
        R1[("raw_airports")]
        R2[("raw_airlines")]
        R3[("raw_routes")]
    end

    subgraph staging["3 · Staging (views, schema: staging)"]
        S1["stg_airports"]
        S2["stg_airlines"]
        S3["stg_routes"]
    end

    subgraph inter["4 · Intermediate (tables, schema: intermediate)"]
        I1["int_routes_enriched<br/>join routes↔airports<br/>haversine_km → distance_km"]
    end

    subgraph marts["5 · Marts (tables, schema: marts)"]
        D1["dim_airport"]
        D2["dim_airline"]
        F1["fct_route"]
        M1["mart_busiest_airports"]
        M2["mart_airline_reach"]
        M3["mart_country_connectivity"]
    end

    DASH["6 · Evidence dashboard<br/>KPIs · charts · maps"]

    OF --> DL --> LD
    LD --> R1 & R2 & R3
    R1 --> S1
    R2 --> S2
    R3 --> S3
    S1 --> I1
    S3 --> I1
    S1 --> D1
    S2 --> D2
    I1 --> F1
    D1 --> M1
    F1 --> M1
    I1 --> M2
    D2 --> M2
    I1 --> M3
    D1 & D2 & F1 & M1 & M2 & M3 --> DASH
```

## Layers

### 1 · Ingestion (`ingestion/`)

- **`sources.py`** declares the three datasets: URL, ordered column names (the
  files have no header row), and target raw table name.
- **`download.py`** fetches each `.dat` file into `data/raw/`, skipping files that
  already exist unless `--force` is passed.
- **`load.py`** reads each file with DuckDB's `read_csv`, converts the literal
  `\N` token to `NULL`, keeps every column as `VARCHAR`, appends a `_loaded_at`
  timestamp, and writes it to the `raw` schema of `transform/aeroflow.duckdb`.
- **`load_snowflake.py`** and **`load_databricks.py`** are the cloud
  equivalents. Both run the exact same DuckDB `read_csv` parse, write each
  dataset to Parquet, upload it (Snowflake: the `RAW.LANDING` internal stage;
  Databricks: the `<catalog>.raw.landing` Unity Catalog volume), and create the
  `raw_*` tables from it with a `_loaded_at` timestamp. The warehouses' own CSV
  readers are avoided because their defaults turn unquoted empty fields into
  `NULL` where DuckDB keeps an empty string.

Loading everything as text keeps ingestion robust: no row is ever rejected for a
bad value, and typing and validation are deferred to the staging models where
they are debuggable in SQL.

### 2 · Raw (`raw` schema)

Verbatim copies of the source files. The only added column is `_loaded_at`, which
dbt **source freshness** watches.

### 3 · Staging (`models/staging/`, views)

One cleaned view per source, 1:1 with the raw table:

- rename to `snake_case`, cast types with `try_cast` (portable across DuckDB,
  Snowflake and Databricks),
- convert empty strings / `\N` to `NULL`,
- normalise categoricals (e.g. the airline `active` flag, which mixes `Y`, `N`
  and a stray lowercase `n`),
- drop structurally broken rows (missing airport ids, self-loop routes).

Materialised as **views** because they are cheap and always reflect the latest
raw load.

### 4 · Intermediate (`models/intermediate/`, tables)

`int_routes_enriched` joins each route to its source and destination airport to
attach coordinates, then computes `distance_km` via the portable
[`haversine_km`](../transform/macros/haversine_km.sql) macro. Inner joins drop
routes that reference unknown airports, guaranteeing a well-defined distance.
Materialised as a **table** because it is the heaviest join and feeds several
marts.

### 5 · Marts (`models/marts/`, tables)

A small star schema plus three analytical marts:

- **`dim_airport`** / **`dim_airline`**: conformed dimensions (with a region
  attribute joined from the `seed_region_lookup` seed).
- **`fct_route`**: the fact table; grain = one row per airline / source /
  destination, with foreign keys to both dimensions and a `distance_km` measure.
- **`mart_busiest_airports`**, **`mart_airline_reach`**,
  **`mart_country_connectivity`**: pre-aggregated answers to the headline
  questions, ready for the dashboard.

### 6 · Visualisation (`dashboard/`)

An Evidence.dev project whose pages are Markdown + SQL querying the `marts`
schema directly from the DuckDB file. See [`dashboard/README.md`](../dashboard/README.md).

## Portability

The warehouse is swappable: [`transform/profiles.yml`](../transform/profiles.yml)
defines a `duckdb` target (default) plus `snowflake` and `databricks` targets that
read credentials from the environment. The models run on DuckDB, Snowflake, or
Databricks by switching that single target, with no SQL changes:

- all SQL sticks to functions every engine shares (`try_cast`, `nullif`, window
  functions), and the one dialect-sensitive piece, the great-circle distance, is
  isolated in a macro using trigonometric functions common to all three;
- the seed declares its columns as `string`, a text type on all three engines;
- the raw source has no hardcoded database, so it follows the active target
  (DuckDB `aeroflow`, `SNOWFLAKE_DATABASE`, or `DATABRICKS_CATALOG`).

Raw loading follows the same switch: `python -m pipeline.cli load --target <target>`
loads DuckDB, Snowflake or Databricks, and `transform --target <target>` builds
on it.

## Orchestration & CI

- **`pipeline/cli.py`** (Typer) exposes `ingest`, `load`, `transform` and `all`,
  runnable as `python -m pipeline.cli all`. `load`, `transform` and `all` take
  `--target` (`duckdb` by default).
- **`.github/workflows/ci.yml`** runs once per pull request and on pushes to
  `main`: install → `ruff check` + `ruff format --check` → ingest + load →
  `dbt build` (models **and** tests) → `sqlfluff lint`. A second job repeats the load and
  build on Databricks, but only when the repository has the `DATABRICKS_HOST`,
  `DATABRICKS_HTTP_PATH` and `DATABRICKS_TOKEN` secrets; otherwise it is skipped.
