-- Route fact table (star-schema centre). Grain: one row per
-- airline / source-airport / destination-airport. Foreign keys point at
-- dim_airline and dim_airport; distance_km is the primary additive-ish measure.
with enriched as (
    select * from {{ ref('int_routes_enriched') }}
)

select
    -- Surrogate primary key over the natural grain.
    {{ dbt_utils.generate_surrogate_key([
        'airline_code', 'source_airport_id', 'destination_airport_id'
    ]) }} as route_id,

    -- Foreign keys.
    airline_id,
    source_airport_id,
    destination_airport_id,

    -- Degenerate / descriptive attributes.
    airline_code,
    source_airport_code,
    destination_airport_code,
    is_codeshare,
    stops,
    equipment,

    -- Measures.
    distance_km
from enriched
