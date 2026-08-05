-- Airline dimension: one row per airline. Grain: airline_id.
with airlines as (
    select * from {{ ref('stg_airlines') }}
)

select
    airline_id,
    airline_name,
    alias,
    iata_code,
    icao_code,
    callsign,
    country,
    active_code,
    is_active
from airlines
