# AeroFlow Data Dictionary

Column-level reference for the mart layer (schema `marts`). Types shown are the
DuckDB types produced by the default build; the equivalent Snowflake types
(`NUMBER`, `FLOAT`, `VARCHAR`, `BOOLEAN`) apply on the `snowflake` target.

Descriptions here mirror the dbt `.yml` documentation, which powers `dbt docs`.

---

## `dim_airport` — airport dimension

**Grain:** one row per airport (`airport_id`).

| Column | Type | Description |
| --- | --- | --- |
| `airport_id` | INTEGER | OpenFlights airport identifier. **Primary key** (not null, unique). |
| `iata_code` | VARCHAR | 3-letter IATA code, or NULL. |
| `icao_code` | VARCHAR | 4-letter ICAO code, or NULL. |
| `airport_name` | VARCHAR | Airport name. |
| `city` | VARCHAR | City served by the airport. |
| `country` | VARCHAR | Country the airport is located in. |
| `region` | VARCHAR | Continental region (from `seed_region_lookup`); one of North America, South America, Europe, Africa, Asia, Oceania, Antarctica, Other. |
| `latitude` | DOUBLE | Decimal latitude in degrees. |
| `longitude` | DOUBLE | Decimal longitude in degrees. |
| `altitude_ft` | INTEGER | Elevation in feet. |
| `timezone_offset_hours` | DOUBLE | UTC offset in hours (may be fractional). |
| `tz_name` | VARCHAR | IANA/Olson time-zone name (e.g. `America/New_York`). |
| `airport_type` | VARCHAR | Record type as published by OpenFlights. |

---

## `dim_airline` — airline dimension

**Grain:** one row per airline (`airline_id`).

| Column | Type | Description |
| --- | --- | --- |
| `airline_id` | INTEGER | OpenFlights airline identifier. **Primary key** (not null, unique). |
| `airline_name` | VARCHAR | Airline name. |
| `alias` | VARCHAR | Alternate airline name, or NULL. |
| `iata_code` | VARCHAR | 2-letter IATA airline code, or NULL. |
| `icao_code` | VARCHAR | 3-letter ICAO airline code, or NULL. |
| `callsign` | VARCHAR | Radio callsign, or NULL. |
| `country` | VARCHAR | Country of registration. |
| `active_code` | VARCHAR | Normalised active flag: `Y` or `N` (accepted values). |
| `is_active` | BOOLEAN | TRUE when the airline is currently active. |

---

## `fct_route` — route fact table

**Grain:** one row per airline / source-airport / destination-airport.
Star-schema centre; foreign keys reference `dim_airline` and `dim_airport`.

| Column | Type | Description |
| --- | --- | --- |
| `route_id` | VARCHAR | Surrogate key over (airline_code, source_airport_id, destination_airport_id). **Primary key** (not null, unique). |
| `airline_id` | INTEGER | FK → `dim_airline.airline_id` (nullable when the operating airline is unknown). |
| `source_airport_id` | INTEGER | FK → `dim_airport.airport_id` (origin). Not null. |
| `destination_airport_id` | INTEGER | FK → `dim_airport.airport_id` (destination). Not null. |
| `airline_code` | VARCHAR | IATA/ICAO code of the operating airline. |
| `source_airport_code` | VARCHAR | Origin airport IATA/ICAO code. |
| `destination_airport_code` | VARCHAR | Destination airport IATA/ICAO code. |
| `is_codeshare` | BOOLEAN | TRUE when the route is operated as a codeshare. Not null. |
| `stops` | INTEGER | Number of intermediate stops (usually 0). |
| `equipment` | VARCHAR | Space-separated aircraft type codes flown on the route. |
| `distance_km` | DOUBLE | Great-circle distance between endpoints, in kilometres. Always > 0 (not null; range- and positivity-tested). |

---

## `mart_busiest_airports` — airport connectivity leaderboard

**Grain:** one row per airport that appears on at least one route (`airport_id`).

| Column | Type | Description |
| --- | --- | --- |
| `airport_id` | INTEGER | Airport identifier. **Primary key** (not null, unique). |
| `iata_code` | VARCHAR | IATA code, or NULL. |
| `airport_name` | VARCHAR | Airport name. |
| `city` | VARCHAR | City served. |
| `country` | VARCHAR | Country. |
| `region` | VARCHAR | Continental region. |
| `latitude` | DOUBLE | Latitude in degrees. |
| `longitude` | DOUBLE | Longitude in degrees. |
| `departure_routes` | BIGINT | Number of distinct routes departing this airport. |
| `arrival_routes` | BIGINT | Number of distinct routes arriving at this airport. |
| `total_routes` | BIGINT | `departure_routes + arrival_routes`. |
| `airport_rank` | BIGINT | Ranking by `total_routes` (1 = busiest). Unique. |

---

## `mart_airline_reach` — per-airline network reach

**Grain:** one row per airline (`airline_id`).

| Column | Type | Description |
| --- | --- | --- |
| `airline_id` | INTEGER | Airline identifier. **Primary key** (not null, unique). |
| `airline_name` | VARCHAR | Airline name. |
| `airline_country` | VARCHAR | Country of registration. |
| `is_active` | BOOLEAN | TRUE when the airline is active. |
| `total_routes` | BIGINT | Number of routes operated. |
| `distinct_destinations` | BIGINT | Number of distinct destination airports served. |
| `distinct_destination_countries` | BIGINT | Number of distinct destination countries served. |
| `avg_route_distance_km` | DOUBLE | Average great-circle route distance, in kilometres. |
| `max_route_distance_km` | DOUBLE | Longest single route distance, in kilometres. |

---

## `mart_country_connectivity` — directed country-to-country connectivity

**Grain:** one row per `(source_country, destination_country)` pair.

| Column | Type | Description |
| --- | --- | --- |
| `source_country` | VARCHAR | Origin country. Not null. |
| `destination_country` | VARCHAR | Destination country. Not null. |
| `is_domestic` | BOOLEAN | TRUE when origin and destination countries are the same. |
| `route_count` | BIGINT | Number of routes from source to destination country. |
| `airline_count` | BIGINT | Number of distinct airlines flying the country pair. |
| `avg_distance_km` | DOUBLE | Average route distance for the pair, in kilometres. |
| `max_distance_km` | DOUBLE | Longest route distance for the pair, in kilometres. |

---

_See [`architecture.md`](architecture.md) for how these tables are built, and the
dbt `.yml` files under `transform/models/` for the machine-readable tests and
descriptions._
