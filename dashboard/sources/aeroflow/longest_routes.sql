select
    route.route_id,
    route.source_airport_code,
    src.airport_name        as source_airport,
    src.city                as source_city,
    src.country             as source_country,
    src.latitude            as source_lat,
    src.longitude           as source_lon,
    route.destination_airport_code,
    dst.airport_name        as destination_airport,
    dst.city                as destination_city,
    dst.country             as destination_country,
    dst.latitude            as destination_lat,
    dst.longitude           as destination_lon,
    route.distance_km
from marts.fct_route as route
inner join marts.dim_airport as src on route.source_airport_id = src.airport_id
inner join marts.dim_airport as dst on route.destination_airport_id = dst.airport_id
order by route.distance_km desc
limit 50
