"""Load and filter census tract shapefiles."""
from pathlib import Path
import geopandas as gpd


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


def get_default_shapefile_path() -> Path:
    """Return the default path to the shapefile in data/raw/."""
    return Path(__file__).parent.parent.parent / "data" / "raw" / "tl_2020_29_tract.shp"
