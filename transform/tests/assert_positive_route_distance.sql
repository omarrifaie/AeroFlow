-- Singular data test: every route in the fact table must have a strictly
-- positive great-circle distance. Self-loops and airports with identical
-- coordinates are filtered upstream, so any row returned here signals a bug in
-- the haversine macro or the staging filters. The test passes when this query
-- returns zero rows.
select
    route_id,
    source_airport_code,
    destination_airport_code,
    distance_km
from {{ ref('fct_route') }}
where distance_km is null
    or distance_km <= 0
