-- Country-to-country connectivity: directed route counts between countries.
-- Grain: (source_country, destination_country). Powers the connectivity table
-- and drives the "most connected country pairs" view on the dashboard.
with routes as (
    select * from {{ ref('int_routes_enriched') }}
)

select
    source_country,
    destination_country,
    (source_country = destination_country) as is_domestic,
    count(*) as route_count,
    count(distinct airline_id) as airline_count,
    round(avg(distance_km), 2) as avg_distance_km,
    round(max(distance_km), 2) as max_distance_km
from routes
where source_country is not null
    and destination_country is not null
group by
    source_country,
    destination_country
