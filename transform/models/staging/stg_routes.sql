-- 1:1 cleaned view over raw routes. Codeshare/stops are typed, and structurally
-- broken rows are dropped: routes with no source or destination airport id, and
-- degenerate self-loops (source == destination) which would produce a zero
-- great-circle distance downstream.
with source as (
    select * from {{ source('openflights', 'raw_routes') }}
),

renamed as (
    select
        nullif(trim(airline), '') as airline_code,
        try_cast(airline_id as integer) as airline_id,
        nullif(trim(source_airport), '') as source_airport_code,
        try_cast(source_airport_id as integer) as source_airport_id,
        nullif(trim(destination_airport), '') as destination_airport_code,
        try_cast(destination_airport_id as integer) as destination_airport_id,
        (upper(trim(codeshare)) = 'Y') as is_codeshare,
        try_cast(stops as integer) as stops,
        nullif(trim(equipment), '') as equipment
    from source
)

select *
from renamed
where source_airport_id is not null
    and destination_airport_id is not null
    and source_airport_id <> destination_airport_id
