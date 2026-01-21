#!/usr/bin/env python3
"""
Main pipeline script for STL Site Optimizer.

Usage:
    python scripts/run_pipeline.py [--generate-candidates N] [--output PATH]

This script:
1. Loads block group geometries from local shapefiles
2. Fetches population and vulnerability data from Snowflake
3. Loads/generates candidate sites
4. Builds and saves an interactive map
"""
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import (
    load_stl_block_groups,
    get_default_block_group_shapefile_path,
    SnowflakeClient,
)
from src.processing import process_tracts, generate_candidates, get_base_sites
from src.visualization import build_stl_map, save_map


def main():
    parser = argparse.ArgumentParser(description="STL Site Optimizer Pipeline")
    parser.add_argument(
        "--generate-candidates",
        type=int,
        metavar="N",
        help="Generate N synthetic candidate sites",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/stl_map.html",
        help="Output path for the map HTML",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    bg_shapefile_path = get_default_block_group_shapefile_path()
    output_path = project_root / args.output

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading block group geometries...")
    block_groups = load_stl_block_groups(bg_shapefile_path)
    print(f"  Loaded {len(block_groups)} block groups")

    print("Computing centroids...")
    block_groups = process_tracts(block_groups)

    # Get candidate sites
    if args.generate_candidates:
        print(f"Generating {args.generate_candidates} candidate sites...")
        candidates = generate_candidates(n=args.generate_candidates)
    else:
        print("Using base candidate sites...")
        candidates = get_base_sites()

    print(f"  Using {len(candidates)} candidate sites")

    # Fetch population and vulnerability data from Snowflake
    print("Fetching block group demographics from Snowflake...")
    try:
        client = SnowflakeClient()
        demographics = client.get_tract_info()
        # Ensure GEOID is string type for merge
        block_groups["GEOID"] = block_groups["GEOID"].astype(str)
        demographics["GEOID"] = demographics["GEOID"].astype(str)
        # Merge demographics and vulnerability data
        block_groups = block_groups.merge(demographics, on="GEOID", how="left")
        print(f"  Merged demographics for {len(block_groups)} block groups")
    except Exception as e:
        print(f"  Warning: Could not fetch from Snowflake: {e}")
        print("  Proceeding with geometry only")

    print("Building map...")
    m = build_stl_map(block_groups, candidates)

    print(f"Saving map to {output_path}...")
    save_map(m, output_path)

    print("Done!")
    print(f"\nOpen {output_path} in a browser to view the map.")


if __name__ == "__main__":
    main()
