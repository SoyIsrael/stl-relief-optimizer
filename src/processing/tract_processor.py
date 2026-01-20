"""Process census tract data: centroids, filtering, and export."""
import json

import geopandas as gpd
import pandas as pd


def compute_centroids(gdf: gpd.GeoDataFrame, projected_crs: int = 26915) -> gpd.GeoDataFrame:
    """
    Compute accurate centroids for tract polygons.

    Projects to a suitable CRS for accurate centroid calculation,
    then converts back to WGS84 (EPSG:4326).

    Args:
        gdf: GeoDataFrame with tract geometries in EPSG:4326
        projected_crs: EPSG code for projection (default: 26915 UTM Zone 15N)

    Returns:
        GeoDataFrame with 'lat' and 'lon' columns added
    """
    gdf = gdf.copy()
    gdf_proj = gdf.to_crs(epsg=projected_crs)
    centroids_proj = gdf_proj.geometry.centroid
    centroids = gpd.GeoSeries(centroids_proj, crs=projected_crs).to_crs(epsg=4326)

    gdf["lat"] = centroids.y
    gdf["lon"] = centroids.x

    return gdf


def process_tracts(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Full processing pipeline for tract data.

    Args:
        gdf: Raw tract GeoDataFrame

    Returns:
        Processed GeoDataFrame with centroids
    """
    return compute_centroids(gdf)


def tracts_to_dataframe(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Convert tract GeoDataFrame to a plain DataFrame with GeoJSON geometry.

    Args:
        gdf: GeoDataFrame with tract data

    Returns:
        DataFrame with GEOID, lat, lon, and geom_geojson columns
    """
    df = gdf[["GEOID", "geometry", "lat", "lon"]].copy()
    df["geom_geojson"] = df.geometry.apply(lambda g: json.dumps(g.__geo_interface__))
    return df.drop(columns=["geometry"])
