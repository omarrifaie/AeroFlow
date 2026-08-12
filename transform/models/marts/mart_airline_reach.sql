-- Airline reach: how far and wide each airline flies. Grain: airline_id.
-- Routes with an unknown airline id are excluded by the inner join.
with routes as (
    select * from {{ ref('int_routes_enriched') }}
),

airlines as (
    select * from {{ ref('dim_airline') }}
)

select
    airlines.airline_id,
    airlines.airline_name,
    airlines.country as airline_country,
    airlines.is_active,
    count(*) as total_routes,
    count(distinct routes.destination_airport_id) as distinct_destinations,
    count(distinct routes.destination_country) as distinct_destination_countries,
    round(avg(routes.distance_km), 2) as avg_route_distance_km,
    max(routes.distance_km) as max_route_distance_km
from routes
inner join airlines
    on routes.airline_id = airlines.airline_id
group by
    airlines.airline_id,
    airlines.airline_name,
    airlines.country,
    airlines.is_active
