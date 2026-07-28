-- 1:1 cleaned view over raw airlines. Normalises the "active" flag (the source
-- mixes 'Y', 'N' and a stray lowercase 'n') into an uppercase code plus a proper
-- boolean, and drops rows without an airline id.
with source as (
    select * from {{ source('openflights', 'raw_airlines') }}
),

renamed as (
    select
        try_cast(airline_id as integer) as airline_id,
        nullif(trim(name), '') as airline_name,
        nullif(trim(alias), '') as alias,
        nullif(trim(iata), '') as iata_code,
        nullif(trim(icao), '') as icao_code,
        nullif(trim(callsign), '') as callsign,
        nullif(trim(country), '') as country,
        upper(nullif(trim(active), '')) as active_code,
        (upper(trim(active)) = 'Y') as is_active
    from source
)

select *
from renamed
where airline_id is not null
