---
title: AeroFlow Routes
description: Longest routes, country connectivity and a route map from AeroFlow.
hide_title: true
---

<Hero page="Routes" />

<p class="hero-lead">Route level analytics from AeroFlow, drawn from the fct_route model and the country connectivity mart.</p>

## Longest routes

<p class="caption">The twenty five longest great circle routes in the network, with both endpoints.</p>

```sql longest
select
    source_airport_code,
    source_city,
    source_country,
    destination_airport_code,
    destination_city,
    destination_country,
    distance_km
from aeroflow.longest_routes
order by distance_km desc
limit 25
```

<DataTable data={longest} rows=25>
    <Column id=source_airport_code title="From" />
    <Column id=source_city title="Origin city" />
    <Column id=destination_airport_code title="To" />
    <Column id=destination_city title="Destination city" />
    <Column id=distance_km title="Distance (km)" fmt="#,##0" contentType=colorscale />
</DataTable>

## Route map

<p class="caption">Endpoints of the fifty longest routes in the AeroFlow network. Origins and destinations are plotted from their airport coordinates.</p>

```sql route_points
select source_airport as airport_name, source_lat as latitude, source_lon as longitude, distance_km
from aeroflow.longest_routes
union all
select destination_airport as airport_name, destination_lat as latitude, destination_lon as longitude, distance_km
from aeroflow.longest_routes
```

<PointMap
    data={route_points}
    lat=latitude
    long=longitude
    value=distance_km
    valueFmt="#,##0"
    pointName=airport_name
    height=500
    startingZoom=1
/>

## Country connectivity

<p class="caption">The most connected country pairs by number of routes, limited to international links.</p>

```sql international_pairs
select
    source_country,
    destination_country,
    route_count,
    airline_count,
    avg_distance_km
from aeroflow.country_connectivity
where is_domestic = false
order by route_count desc
limit 25
```

<DataTable data={international_pairs} rows=25>
    <Column id=source_country title="From country" />
    <Column id=destination_country title="To country" />
    <Column id=route_count title="Routes" fmt="#,##0" contentType=colorscale />
    <Column id=airline_count title="Airlines" fmt="#,##0" />
    <Column id=avg_distance_km title="Avg distance (km)" fmt="#,##0" />
</DataTable>

<p class="caption">How the whole network splits between domestic and international routes.</p>

```sql domestic_split
select
    case when is_domestic then 'Domestic' else 'International' end as route_type,
    sum(route_count) as routes
from aeroflow.country_connectivity
group by 1
order by routes desc
```

<BarChart
    data={domestic_split}
    x=route_type
    y=routes
/>

---

<p class="footer-note">AeroFlow is built as code on the OpenFlights network. Data: OpenFlights, licensed under the Open Database License (ODbL).</p>
