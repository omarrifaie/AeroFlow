select
    (select count(*) from marts.dim_airport)                    as total_airports,
    (select count(*) from marts.dim_airline)                    as total_airlines,
    (select count(*) from marts.fct_route)                      as total_routes,
    (select round(avg(distance_km), 0) from marts.fct_route)    as avg_route_distance_km,
    (select round(max(distance_km), 0) from marts.fct_route)    as longest_route_km
