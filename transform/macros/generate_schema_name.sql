{#
    Use the custom schema name verbatim instead of dbt's default behaviour of
    prefixing it with the target schema (e.g. "main_marts"). This gives clean,
    predictable schema names -- staging / intermediate / marts -- that the
    Evidence dashboard and ad-hoc SQL can rely on. Models without a +schema
    config fall back to the target's configured schema.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
