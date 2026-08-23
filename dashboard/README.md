# AeroFlow Dashboard (Evidence.dev)

A "BI-as-code" dashboard built with [Evidence](https://evidence.dev). Every page
is Markdown with embedded SQL that queries the DuckDB marts produced by the dbt
project in `../transform`.

## Prerequisites

- **Node 18+** and npm.
- The warehouse must already be built. From the repository root run:

  ```bash
  make all        # or: python -m pipeline.cli all
  ```

  This creates `../transform/aeroflow.duckdb` with the `marts` schema the
  dashboard reads (see `sources/aeroflow/connection.yaml`).

## Run it

```bash
cd dashboard
npm install       # first time only
npm run sources   # materialise the source queries from DuckDB
npm run dev       # start the dev server at http://localhost:3000
```

To produce a static build instead:

```bash
npm run build     # outputs to build/
npm run preview
```

## Pages

| Page          | Contents                                                        |
| ------------- | --------------------------------------------------------------- |
| `index.md`    | Headline KPIs and top-airport / top-airline bar charts.         |
| `airports.md` | Busiest-airport leaderboard, bar chart and a world points map.  |
| `routes.md`   | Longest routes, a route map and country-to-country connectivity.|

## Data sources

The DuckDB connection is defined in `sources/aeroflow/`. Each `.sql` file there
becomes a queryable table (`aeroflow.<name>`) that the pages select from.

---

_Data: OpenFlights, licensed under the Open Database License (ODbL)._
