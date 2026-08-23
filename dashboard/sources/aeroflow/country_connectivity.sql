select
    source_country,
    destination_country,
    is_domestic,
    route_count,
    airline_count,
    avg_distance_km,
    max_distance_km
from marts.mart_country_connectivity
order by route_count desc
