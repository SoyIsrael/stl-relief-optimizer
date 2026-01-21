"""Build interactive Folium maps for STL site visualization."""
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd

# St. Louis center coordinates
STL_CENTER = (38.6270, -90.1994)


def _build_popup_text(row: pd.Series) -> str:
    """Build HTML popup text with available demographics."""
    html = f"<b>GEOID:</b> {row.get('GEOID', 'N/A')}<br>"

    if "Location" in row:
        html += f"<b>Location:</b> {row['Location']}<br>"

    # Population and key vulnerability metrics
    fields = ["POP", "Median_HH_Income", "Low_Income_Rate", "Child_Dependency_Rate",
              "Elderly_Dependency_Rate", "Renter_Rate", "Vacancy_Rate", "No_Internet_Rate"]

    for field in fields:
        if field in row and pd.notna(row[field]):
            value = row[field]
            if isinstance(value, float):
                if "Rate" in field:
                    value = f"{value:.1%}"
                else:
                    value = f"{value:,.0f}"
            html += f"<b>{field}:</b> {value}<br>"

    return html


def build_stl_map(
    block_groups: gpd.GeoDataFrame,
    candidate_sites: pd.DataFrame | None = None,
    center: tuple = STL_CENTER,
    zoom_start: int = 11,
    show_centroids: bool = True,
) -> folium.Map:
    """
    Build an interactive Folium map of St. Louis block groups and candidate sites.

    Args:
        block_groups: GeoDataFrame with block group geometries and demographics
        candidate_sites: DataFrame with site_id, lat, lon columns
        center: Map center coordinates (lat, lon)
        zoom_start: Initial zoom level
        show_centroids: Whether to show block group centroid markers

    Returns:
        Folium Map object
    """
    m = folium.Map(
        location=list(center),
        zoom_start=zoom_start,
        tiles="cartodbpositron",
    )

    # Add block group polygons with popup showing demographics
    for _, row in block_groups.iterrows():
        popup_text = _build_popup_text(row)
        folium.GeoJson(
            gpd.GeoSeries(row.geometry).__geo_interface__,
            style_function=lambda x: {
                "fillColor": "#ff7800",
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.3,
            },
            popup=folium.Popup(popup_text, max_width=300),
        ).add_to(m)

    # Add block group centroids
    if show_centroids and "lat" in block_groups.columns:
        for _, row in block_groups.iterrows():
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
