# AeroFlow ✈️

[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![dbt](https://img.shields.io/badge/dbt-1.8%2B-FF694B?logo=dbt&logoColor=white)](transform/)
[![DuckDB](https://img.shields.io/badge/DuckDB-warehouse-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org)
[![Evidence](https://img.shields.io/badge/Evidence.dev-dashboard-7C3AED)](dashboard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**AeroFlow** is an end-to-end analytics-engineering pipeline over the global
flight network. It ingests the free [OpenFlights](https://openflights.org/data.html)
datasets, loads them into a local **DuckDB** warehouse, transforms them with
**dbt** (staging → intermediate → marts, fully tested and documented),
orchestrates the whole thing behind a small **Typer CLI**, validates every change
in **GitHub Actions CI**, and visualises the results with an **Evidence.dev**
"BI-as-code" dashboard. The same dbt models run on **Snowflake** by switching a
single target - so this repo doubles as a portable ELT reference.

> Built by **Omar Rifaie**.

---

## Screenshots

![AeroFlow demo](docs/img/demo.gif)

| Overview | Airports | Routes |
| --- | --- | --- |
| ![Overview KPIs](docs/img/dashboard-overview.png) | ![Busiest airports](docs/img/dashboard-airports.png) | ![Routes & connectivity](docs/img/dashboard-routes.png) |

---

## Architecture

```mermaid
flowchart LR
    subgraph src["Source (free, no auth)"]
        OF["OpenFlights .dat files<br/>airports · airlines · routes"]
    end

    subgraph py["Ingestion — Python"]
        DL["download.py<br/>data/raw/"]
        LD["load.py<br/>\\N → NULL, all VARCHAR"]
    end

    subgraph wh["Warehouse — DuckDB (aeroflow.duckdb)"]
        RAW[("raw<br/>raw_airports<br/>raw_airlines<br/>raw_routes")]
    end

    subgraph dbt["Transform — dbt"]
        STG["staging<br/>views · typed · cleaned"]
        INT["intermediate<br/>int_routes_enriched<br/>+ haversine_km"]
        MRT["marts<br/>dim_airport · dim_airline · fct_route<br/>mart_busiest_airports<br/>mart_airline_reach<br/>mart_country_connectivity"]
    end

    subgraph bi["Visualise — Evidence.dev"]
        DASH["index · airports · routes<br/>KPIs · charts · maps"]
    end

    OF --> DL --> LD --> RAW --> STG --> INT --> MRT --> DASH

    CLI["pipeline.cli<br/>ingest · load · transform · all"] -.orchestrates.-> DL
    CI["GitHub Actions CI<br/>ruff · dbt build · sqlfluff"] -.validates.-> dbt
```

Data flows one way - **ingest → load → transform → visualise** — with tests and
lint gates at every boundary. See [`docs/architecture.md`](docs/architecture.md)
for a layer-by-layer breakdown and [`docs/data_dictionary.md`](docs/data_dictionary.md)
for every mart column.

---

## Stack

| Layer            | Tooling                                                        |
| ---------------- | ------------------------------------------------------------- |
| Ingestion        | Python 3.11+, `requests`, `duckdb`                            |
| Orchestration    | `typer` CLI (`python -m pipeline.cli`)                        |
| Warehouse        | DuckDB locally · Snowflake by switching the dbt target       |
| Transformations  | `dbt-core` + `dbt-duckdb`, `dbt_utils`, `dbt_expectations`   |
| Quality gates    | `ruff` (Python), `sqlfluff` (SQL), `pre-commit`, GitHub CI   |
| Dashboard        | Evidence.dev (Node 18+)                                       |

---

## Prerequisites

- **Python 3.11+**
- **Node 18+** (only for the dashboard)
- No cloud account and no API keys required - the data source is public and the
  default warehouse is a local DuckDB file.

---

## Quickstart

```bash
# 1. Set up the Python environment and install dependencies
make setup

# 2. Run the full pipeline: download -> load -> dbt build (models + tests)
make all

# 3. Explore the data in the Evidence dashboard (http://localhost:3000)
make dashboard
```

Prefer to skip `make`? The equivalent commands are:

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pipeline.cli all
cd dashboard && npm install && npm run dev
```

### Individual steps

```bash
python -m pipeline.cli ingest       # download raw .dat files to data/raw/
python -m pipeline.cli load         # load into DuckDB schema `raw`
python -m pipeline.cli transform    # dbt deps + dbt build
python -m pipeline.cli all          # all of the above, in order
```

---

## Run it on Snowflake

The dbt models are written in portable, ANSI/Snowflake-compatible SQL. To build
the exact same project on Snowflake instead of DuckDB:

```bash
cp .env.example .env      # then fill in your Snowflake details
set -a && . ./.env && set +a

cd transform
dbt deps
dbt build --target snowflake
```

The `snowflake` target in [`transform/profiles.yml`](transform/profiles.yml)
reads `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`,
`SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE` and
`SNOWFLAKE_SCHEMA` from the environment. No model SQL changes are required - only
the target switches.

---

## Project layout

```
aeroflow/
├── ingestion/     # download + load OpenFlights -> DuckDB (schema raw)
├── pipeline/      # Typer CLI orchestrating ingest/load/transform/all
├── transform/     # dbt project: staging -> intermediate -> marts (+ tests, macros, seeds)
├── dashboard/     # Evidence.dev BI-as-code dashboard
├── docs/          # architecture + data dictionary
└── .github/       # CI workflow
```

---

## Testing & quality

Every `dbt build` runs the models **and** the data tests:

- `not_null` / `unique` on all keys, `relationships` from `fct_route` to the
  dimensions, `accepted_values` on categorical columns.
- `dbt_expectations` assertions (non-empty fact table, distances within
  physically plausible bounds).
- A singular test (`assert_positive_route_distance`) guaranteeing every route
  distance is strictly positive.
- Source **freshness** configured on the raw load timestamp.

Linting runs in CI and via `pre-commit`:

```bash
make lint          # ruff (Python) + sqlfluff (SQL)
pre-commit install # optional: run the gates on every commit
```

---

## Data & license

- **Data:** [OpenFlights](https://openflights.org/data.html) airports, airlines
  and routes. © OpenFlights contributors, distributed under the
  [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/1-0/).
  AeroFlow downloads these files at run time and does not redistribute them.
- **Code:** MIT - see [LICENSE](LICENSE).
