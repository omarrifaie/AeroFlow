select
    airport_rank,
    iata_code,
    airport_name,
    city,
    country,
    region,
    latitude,
    longitude,
    departure_routes,
    arrival_routes,
    total_routes
from marts.mart_busiest_airports
order by airport_rank
