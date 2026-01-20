#!/usr/bin/env python3
"""
Main pipeline script for STL Site Optimizer.

Usage:
    python scripts/run_pipeline.py [--use-snowflake] [--generate-candidates N]

This script:
1. Loads tract geometries from local shapefiles
2. Fetches tract population data (from Census API or Snowflake)
3. Loads/generates candidate sites
4. Builds and saves an interactive map
"""
import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import load_stl_tracts, fetch_stl_tract_info, SnowflakeClient
from src.processing import process_tracts, generate_candidates, get_base_sites
from src.visualization import build_stl_map, save_map


def main():
    parser = argparse.ArgumentParser(description="STL Site Optimizer Pipeline")
    parser.add_argument(
        "--use-snowflake",
        action="store_true",
        help="Load candidate sites and tract info from Snowflake",
    )
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
    shapefile_path = project_root / "data" / "raw" / "tl_2020_29_tract.shp"
    output_path = project_root / args.output

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Loading tract geometries...")
    tracts = load_stl_tracts(shapefile_path)
    print(f"  Loaded {len(tracts)} tracts")

    print("Computing centroids...")
    tracts = process_tracts(tracts)

    # Get candidate sites
    if args.generate_candidates:
        print(f"Generating {args.generate_candidates} candidate sites...")
        candidates = generate_candidates(n=args.generate_candidates)
    elif args.use_snowflake:
        print("Fetching candidate sites from Snowflake...")
        client = SnowflakeClient()
        candidates = client.get_candidate_sites()
    else:
        print("Using base candidate sites...")
        candidates = get_base_sites()

    print(f"  Using {len(candidates)} candidate sites")

    # Optionally fetch tract info for population data
    if args.use_snowflake:
        print("Fetching tract info from Snowflake...")
        tract_info = client.get_tract_info()
        tracts = tracts.merge(tract_info[["GEOID", "POP"]], on="GEOID", how="left")

    print("Building map...")
    m = build_stl_map(tracts, candidates)

    print(f"Saving map to {output_path}...")
    save_map(m, output_path)

    print("Done!")
    print(f"\nOpen {output_path} in a browser to view the map.")


if __name__ == "__main__":
    main()
