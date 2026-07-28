-- 1:1 cleaned view over raw airports: snake_case names, typed columns, blanks
-- and the OpenFlights "\N" token normalised to NULL, and structurally broken
-- rows (missing airport id) dropped. try_cast keeps the model resilient to the
-- odd unparseable value; it exists with identical semantics on DuckDB and Snowflake.
with source as (
    select * from {{ source('openflights', 'raw_airports') }}
),

renamed as (
    select
        try_cast(airport_id as integer) as airport_id,
        nullif(trim(name), '') as airport_name,
        nullif(trim(city), '') as city,
        nullif(trim(country), '') as country,
        nullif(trim(iata), '') as iata_code,
        nullif(trim(icao), '') as icao_code,
        try_cast(latitude as double) as latitude,
        try_cast(longitude as double) as longitude,
        try_cast(altitude as integer) as altitude_ft,
        try_cast(timezone as double) as timezone_offset_hours,
        nullif(trim(dst), '') as dst,
        nullif(trim(tz_database_time_zone), '') as tz_name,
        nullif(trim(type), '') as airport_type,
        nullif(trim(source), '') as data_source
    from source
)

select *
from renamed
where airport_id is not null
