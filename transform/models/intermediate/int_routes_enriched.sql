-- Enrich each route with its source and destination airport attributes and the
-- great-circle distance between them. Inner joins guarantee both endpoints
-- exist (routes referencing unknown airports are dropped), so distance_km is
-- always well defined. Materialised as a table -- it is the heaviest join in the
-- project and feeds several marts.
with routes as (
    select * from {{ ref('stg_routes') }}
),

airports as (
    select
        airport_id,
        iata_code,
        airport_name,
        city,
        country,
        latitude,
        longitude
    from {{ ref('stg_airports') }}
),

joined as (
    select
        routes.airline_code,
        routes.airline_id,

        routes.source_airport_id,
        routes.source_airport_code,
        src.airport_name        as source_airport_name,
        src.city                as source_city,
        src.country             as source_country,
        src.latitude            as source_latitude,
        src.longitude           as source_longitude,

        routes.destination_airport_id,
        routes.destination_airport_code,
        dst.airport_name        as destination_airport_name,
        dst.city                as destination_city,
        dst.country             as destination_country,
        dst.latitude            as destination_latitude,
        dst.longitude           as destination_longitude,

        routes.is_codeshare,
        routes.stops,
        routes.equipment
    from routes
    inner join airports as src
        on routes.source_airport_id = src.airport_id
    inner join airports as dst
        on routes.destination_airport_id = dst.airport_id
)

select
    *,
    round(
        {{ haversine_km('source_latitude', 'source_longitude',
                        'destination_latitude', 'destination_longitude') }},
        2
    ) as distance_km
from joined
