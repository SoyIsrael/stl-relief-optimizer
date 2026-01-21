"""Load and filter census tract and block group shapefiles or from Snowflake."""
from pathlib import Path
import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape


def load_stl_tracts(
    shapefile_path: str | Path,
    city_fips: str = "510",
    county_fips: str = "189",
) -> gpd.GeoDataFrame:
    """
    Load Missouri census tracts and filter to St. Louis City/County.

    Args:
        shapefile_path: Path to the tl_2020_29_tract.shp file
        city_fips: FIPS code for St. Louis City (default: "510")
        county_fips: FIPS code for St. Louis County (default: "189")

    Returns:
        GeoDataFrame of St. Louis tracts in EPSG:4326
    """
    tracts = gpd.read_file(shapefile_path)

    stl = tracts[
        (tracts["COUNTYFP"] == city_fips) | (tracts["COUNTYFP"] == county_fips)
    ].copy()

    return stl.to_crs(epsg=4326)


def load_stl_block_groups(
    shapefile_path: str | Path,
    city_fips: str = "510",
    county_fips: str = "189",
) -> gpd.GeoDataFrame:
    """
    Load Missouri census block groups and filter to St. Louis City/County.

    Args:
        shapefile_path: Path to the tl_2020_29_bg.shp file
        city_fips: FIPS code for St. Louis City (default: "510")
        county_fips: FIPS code for St. Louis County (default: "189")

    Returns:
        GeoDataFrame of St. Louis block groups in EPSG:4326
    """
    bgs = gpd.read_file(shapefile_path)

    stl = bgs[
        (bgs["COUNTYFP"] == city_fips) | (bgs["COUNTYFP"] == county_fips)
    ].copy()

    return stl.to_crs(epsg=4326)


def get_default_shapefile_path() -> Path:
    """Return the default path to the tract shapefile in data/raw/."""
    return Path(__file__).parent.parent.parent / "data" / "raw" / "tl_2020_29_tract.shp"


def get_default_block_group_shapefile_path() -> Path:
    """Return the default path to the block group shapefile in data/raw/."""
    return Path(__file__).parent.parent.parent / "data" / "raw" / "tl_2020_29_bg.shp"


def load_stl_block_groups_from_snowflake() -> gpd.GeoDataFrame:
    """
    Load block group boundaries from Snowflake.

    Returns:
        GeoDataFrame of St. Louis block groups with geometry and centroids
    """
    from .snowflake_client import SnowflakeClient

    client = SnowflakeClient()
    boundaries_df = client.get_boundaries()

    # Reconstruct geometry from GeoJSON
    geometries = []
    for _, row in boundaries_df.iterrows():
        geom_dict = json.loads(row["geom_geojson"]) if isinstance(row["geom_geojson"], str) else row["geom_geojson"]
        geometries.append(shape(geom_dict))

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        boundaries_df.drop(columns=["geom_geojson"]),
        geometry=geometries,
        crs="EPSG:4326",
    )

    return gdf
