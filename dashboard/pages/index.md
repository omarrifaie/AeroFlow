---
title: AeroFlow
description: Airports, airlines and routes across the world, built as code with AeroFlow.
hide_title: true
---

<Hero page="Home" />

<p class="hero-lead">AeroFlow turns the raw OpenFlights network into a tested, documented analytics warehouse. Every figure on these pages is computed by the dbt marts under transform and read straight from DuckDB, with no manual spreadsheets and no charts drawn by hand.</p>

```sql kpis
select * from aeroflow.kpis
```

<div class="kpi-cards">
<Grid cols=5>
    <BigValue data={kpis} value=total_airports title="Airports" fmt="#,##0" />
    <BigValue data={kpis} value=total_airlines title="Airlines" fmt="#,##0" />
    <BigValue data={kpis} value=total_routes title="Routes" fmt="#,##0" />
    <BigValue data={kpis} value=avg_route_distance_km title="Avg distance (km)" fmt="#,##0" />
    <BigValue data={kpis} value=longest_route_km title="Longest route (km)" fmt="#,##0" />
</Grid>
</div>

## Busiest airports

<p class="caption">The ten most connected airports in the AeroFlow network, counting departures plus arrivals.</p>

```sql top_airports
select
    iata_code,
    airport_name,
    city,
    country,
    total_routes
from aeroflow.busiest_airports
order by total_routes desc
limit 10
```

<BarChart
    data={top_airports}
    x=iata_code
    y=total_routes
    swapXY=true
/>

## Airlines with the widest reach

<p class="caption">The ten airlines that reach the most routes across the whole AeroFlow network.</p>

```sql top_airlines
select
    airline_name,
    total_routes,
    distinct_destination_countries
from aeroflow.airline_reach
order by total_routes desc
limit 10
```

<BarChart
    data={top_airlines}
    x=airline_name
    y=total_routes
    swapXY=true
/>

## Explore further

<p class="caption">Two focused AeroFlow views go deeper into the network.</p>

- [Airports](/airports): the full connectivity leaderboard, a bar chart and a world map.
- [Routes](/routes): the longest routes, country to country connectivity and a route map.

---

<p class="footer-note">AeroFlow is built as code on the OpenFlights network. Data: OpenFlights, licensed under the Open Database License (ODbL).</p>
