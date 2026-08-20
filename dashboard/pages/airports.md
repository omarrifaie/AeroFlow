---
title: AeroFlow Airports
description: Busiest airports leaderboard, bar chart and world map from AeroFlow.
hide_title: true
---

<Hero page="Airports" />

<p class="hero-lead">AeroFlow maps airport connectivity across the whole OpenFlights network, served straight from the busiest airports mart.</p>

```sql busiest
select
    airport_rank,
    iata_code,
    airport_name,
    city,
    country,
    region,
    departure_routes,
    arrival_routes,
    total_routes,
    latitude,
    longitude
from aeroflow.busiest_airports
order by airport_rank
limit 200
```

## Leaderboard

<p class="caption">The twenty five busiest airports, with departures and arrivals broken out and coloured by total routes.</p>

```sql busiest_table
select
    airport_rank,
    iata_code,
    airport_name,
    city,
    country,
    region,
    departure_routes,
    arrival_routes,
    total_routes
from aeroflow.busiest_airports
order by airport_rank
limit 25
```

<DataTable data={busiest_table} rows=25>
    <Column id=airport_rank title="#" />
    <Column id=iata_code title="IATA" />
    <Column id=airport_name title="Airport" />
    <Column id=city title="City" />
    <Column id=country title="Country" />
    <Column id=region title="Region" />
    <Column id=departure_routes title="Departures" fmt="#,##0" />
    <Column id=arrival_routes title="Arrivals" fmt="#,##0" />
    <Column id=total_routes title="Total" fmt="#,##0" contentType=colorscale />
</DataTable>

## Top 20 by total routes

<p class="caption">The twenty most connected airports, measured by total routes.</p>

```sql top20
select
    iata_code,
    city,
    total_routes
from aeroflow.busiest_airports
order by total_routes desc
limit 20
```

<BarChart
    data={top20}
    x=iata_code
    y=total_routes
    swapXY=true
/>

## World map

<p class="caption">Every airport in the AeroFlow network that appears on at least one route, sized by total connectivity. Zoom in to explore regional hubs.</p>

<PointMap
    data={busiest}
    lat=latitude
    long=longitude
    value=total_routes
    valueFmt="#,##0"
    pointName=airport_name
    height=500
    startingZoom=1
/>

---

<p class="footer-note">AeroFlow is built as code on the OpenFlights network. Data: OpenFlights, licensed under the Open Database License (ODbL).</p>
