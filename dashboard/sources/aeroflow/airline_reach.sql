select
    airline_name,
    airline_country,
    is_active,
    total_routes,
    distinct_destinations,
    distinct_destination_countries,
    avg_route_distance_km,
    max_route_distance_km
from marts.mart_airline_reach
order by total_routes desc
