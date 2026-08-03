{#
    Great-circle distance in kilometres between two lat/lon points.

    Uses the haversine formula with a mean Earth radius of 6371 km. Every
    function used here -- radians, sin, cos, asin, sqrt, power, least -- exists
    with identical semantics on both DuckDB and Snowflake, so the calling models
    are portable across targets with no changes.

    The inner sqrt result is clamped to 1.0 with least() to keep asin() inside
    its valid [-1, 1] domain in the (rare) event of floating-point overshoot for
    near-antipodal coordinates.

    Args are expected to be numeric degrees (already cast in staging).
#}
{% macro haversine_km(lat1, lon1, lat2, lon2) %}
(
    2 * 6371.0 * asin(
        least(
            1.0,
            sqrt(
                power(sin(radians(({{ lat2 }} - {{ lat1 }}) / 2.0)), 2)
                + cos(radians({{ lat1 }}))
                * cos(radians({{ lat2 }}))
                * power(sin(radians(({{ lon2 }} - {{ lon1 }}) / 2.0)), 2)
            )
        )
    )
)
{% endmacro %}
