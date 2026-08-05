-- Airport dimension: one row per airport, enriched with a continental region
-- from the region seed. Grain: airport_id.
with airports as (
    select * from {{ ref('stg_airports') }}
),

regions as (
    select
        country,
        region
    from {{ ref('seed_region_lookup') }}
)

select
    airports.airport_id,
    airports.iata_code,
    airports.icao_code,
    airports.airport_name,
    airports.city,
    airports.country,
    coalesce(regions.region, 'Other') as region,
    airports.latitude,
    airports.longitude,
    airports.altitude_ft,
    airports.timezone_offset_hours,
    airports.tz_name,
    airports.airport_type
from airports
left join regions
    on airports.country = regions.country
