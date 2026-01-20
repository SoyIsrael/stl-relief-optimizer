"""Build interactive Folium maps for STL site visualization."""
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd

# St. Louis center coordinates
STL_CENTER = (38.6270, -90.1994)


def build_stl_map(
    tracts: gpd.GeoDataFrame,
    candidate_sites: pd.DataFrame | None = None,
    center: tuple = STL_CENTER,
    zoom_start: int = 11,
    show_centroids: bool = True,
) -> folium.Map:
    """
    Build an interactive Folium map of St. Louis tracts and candidate sites.

    Args:
        tracts: GeoDataFrame with tract geometries (must have lat/lon for centroids)
        candidate_sites: DataFrame with site_id, lat, lon columns
        center: Map center coordinates (lat, lon)
        zoom_start: Initial zoom level
        show_centroids: Whether to show tract centroid markers

    Returns:
        Folium Map object
    """
    m = folium.Map(
        location=list(center),
        zoom_start=zoom_start,
        tiles="cartodbpositron",
    )

    # Add tract polygons
    folium.GeoJson(
        tracts,
        style_function=lambda x: {
            "fillColor": "#ff7800",
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.3,
        },
        tooltip=folium.GeoJsonTooltip(fields=["GEOID"]),
    ).add_to(m)

    # Add tract centroids
    if show_centroids and "lat" in tracts.columns:
        for _, row in tracts.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=2,
                color="red",
                fill=True,
                fill_opacity=0.6,
            ).add_to(m)

    # Add candidate sites
    if candidate_sites is not None:
        for _, site in candidate_sites.iterrows():
            folium.Marker(
                location=[site["lat"], site["lon"]],
                icon=folium.Icon(color="blue", icon="plus-sign"),
                popup=site.get("site_id", "Site"),
            ).add_to(m)

    return m


def save_map(m: folium.Map, output_path: str | Path) -> None:
    """Save a Folium map to an HTML file."""
    m.save(str(output_path))
