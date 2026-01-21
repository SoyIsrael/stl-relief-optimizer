#!/usr/bin/env python3
"""
Upload block group boundaries to Snowflake.

Usage:
    python scripts/upload_boundaries.py

Loads block group geometries from local shapefile and uploads to Snowflake
for centralized geospatial data management.
"""
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import load_stl_block_groups, get_default_block_group_shapefile_path, SnowflakeClient


def main():
    project_root = Path(__file__).parent.parent
    shapefile_path = get_default_block_group_shapefile_path()

    if not shapefile_path.exists():
        print(f"Error: {shapefile_path} not found")
        sys.exit(1)

    print(f"Loading block group geometries from {shapefile_path}...")
    block_groups = load_stl_block_groups(shapefile_path)
    print(f"  Loaded {len(block_groups)} block groups")

    # Extract geometry as GeoJSON and add lat/lon for quick access
    print("Processing geometries...")
    data = []
    for _, row in block_groups.iterrows():
        centroid = row.geometry.centroid
        data.append({
            "GEOID": str(row["GEOID"]),
            "STATEFP": row["STATEFP"],
            "COUNTYFP": row["COUNTYFP"],
            "TRACTCE": row["TRACTCE"],
            "BLKGRPCE": row["BLKGRPCE"],
            "lat": centroid.y,
            "lon": centroid.x,
            "geom_geojson": row.geometry.__geo_interface__,
        })

    df = pd.DataFrame(data)
    print(f"  Processed {len(df)} geometries")

    print("Connecting to Snowflake...")
    client = SnowflakeClient()

    print("Uploading to BLOCK_GROUP_BOUNDARIES table...")
    client.write_table(df, "BLOCK_GROUP_BOUNDARIES", if_exists="replace")
    print(f"  Successfully uploaded {len(df)} rows to BLOCK_GROUP_BOUNDARIES table")

    print("\nDone! Block group boundaries are now in Snowflake.")


if __name__ == "__main__":
    main()
