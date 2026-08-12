-- Busiest airports: departing + arriving route counts per airport, ranked by
-- total connectivity. Grain: airport_id (airports that appear on at least one
-- route). Feeds the dashboard's airport leaderboard and points map.
with routes as (
    select * from {{ ref('fct_route') }}
),

airports as (
    select * from {{ ref('dim_airport') }}
),

departures as (
    select
        source_airport_id as airport_id,
        count(*) as departure_routes
    from routes
    group by 1
),

arrivals as (
    select
        destination_airport_id as airport_id,
        count(*) as arrival_routes
    from routes
    group by 1
),

combined as (
    select
        airports.airport_id,
        airports.iata_code,
        airports.airport_name,
        airports.city,
        airports.country,
        airports.region,
        airports.latitude,
        airports.longitude,
        coalesce(departures.departure_routes, 0) as departure_routes,
        coalesce(arrivals.arrival_routes, 0) as arrival_routes,
        coalesce(departures.departure_routes, 0)
        + coalesce(arrivals.arrival_routes, 0) as total_routes
    from airports
    left join departures on airports.airport_id = departures.airport_id
    left join arrivals on airports.airport_id = arrivals.airport_id
)

select
    *,
    row_number() over (order by total_routes desc, airport_id asc) as airport_rank
from combined
where total_routes > 0
