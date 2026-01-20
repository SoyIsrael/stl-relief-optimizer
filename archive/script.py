import geopandas as gpd
import folium

# Load Missouri census tracts
tracts = gpd.read_file("tl_2020_29_tract.shp")
candidate_sites = [
    {"id": "church_1", "lat": 38.6359, "lon": -90.2211},  # Central West End
    {"id": "church_2", "lat": 38.6277, "lon": -90.1994},  # Downtown
    {"id": "school_1", "lat": 38.6460, "lon": -90.2547},  # Delmar Loop
    {"id": "school_2", "lat": 38.6089, "lon": -90.2368},  # Tower Grove
    {"id": "community_1", "lat": 38.6701, "lon": -90.2846},  # Clayton edge
    {"id": "community_2", "lat": 38.5964, "lon": -90.2253},  # South City
]


# Filter to St. Louis City + County
stl = tracts[
    (tracts["COUNTYFP"] == "510") |  # St. Louis City
    (tracts["COUNTYFP"] == "189")    # St. Louis County
]

stl = stl.to_crs(epsg=4326)

# Project for accurate centroid computation
stl_proj = stl.to_crs(epsg=26915)

# Compute centroids in projected CRS
centroids_proj = stl_proj.geometry.centroid

# Convert centroids back to lat/lon
centroids = gpd.GeoSeries(centroids_proj, crs=26915).to_crs(epsg=4326)

stl["lat"] = centroids.y
stl["lon"] = centroids.x
print(stl)

m = folium.Map(
    location=[38.6270, -90.1994],  # STL center
    zoom_start=11,
    tiles="cartodbpositron"
)


folium.GeoJson(
    stl,
    style_function=lambda x: {
        "fillColor": "#ff7800",
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.3,
    },
    tooltip=folium.GeoJsonTooltip(fields=["GEOID"])
).add_to(m)

for _, row in stl.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=2,
        color="red",
        fill=True,
        fill_opacity=0.6,
    ).add_to(m)

for site in candidate_sites:
    folium.Marker(
        location=[site["lat"], site["lon"]],
        icon=folium.Icon(color="blue", icon="plus-sign"),
        popup=site["id"]
    ).add_to(m)



m.save("stl_relief_map.html")

print(len(stl))
print(stl.head()[["GEOID", "lat", "lon"]])
print(stl.total_bounds)

stl_poly = stl[["GEOID", "geometry", "lat", "lon"]].copy()
stl_poly["geom_geojson"] = stl_poly.geometry.to_json()  # not ideal per-row

# Better per-row GeoJSON:
import json
stl_poly["geom_geojson"] = stl_poly.geometry.apply(lambda g: json.dumps(g.__geo_interface__))

stl_out = stl_poly.drop(columns=["geometry"])
stl_out.to_csv("demand_tracts.csv", index=False)

import pandas as pd
pd.DataFrame(candidate_sites).rename(columns={"id":"site_id"}).to_csv("candidate_sites.csv", index=False)
