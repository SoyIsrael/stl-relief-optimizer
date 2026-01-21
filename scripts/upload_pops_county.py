#!/usr/bin/env python3
"""
Upload St. Louis County demographics to Snowflake.

Usage:
    python scripts/upload_pops_county.py [input_file]

Default input: data/backup/POPS_COUNTY.csv
Target table: BLOCK_GROUP_DEMOGRAPHICS_COUNTY
"""
import sys
from pathlib import Path
import pandas as pd
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import SnowflakeClient


def main():
    parser = argparse.ArgumentParser(description="Upload St. Louis County demographics to Snowflake")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="data/backup/POPS_COUNTY.csv",
        help="Path to POPS_COUNTY.csv file",
    )
    parser.add_argument(
        "--table",
        type=str,
        default="BLOCK_GROUP_DEMOGRAPHICS_COUNTY",
        help="Target Snowflake table name",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing table instead of appending",
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    input_path = project_root / args.input_file

    # Validate input file
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    print(f"Reading {input_path}...")
    df = pd.read_csv(input_path)
    print(f"  Loaded {len(df)} rows")

    # Ensure GEOID is string
    df["GEOID"] = df["GEOID"].astype(str)

    print(f"\nConnecting to Snowflake...")
    try:
        client = SnowflakeClient()

        if_exists = "replace" if args.replace else "append"
        print(f"Uploading to {args.table} ({if_exists} mode)...")
        client.write_table(df, args.table, if_exists=if_exists)

        print(f"[SUCCESS] Uploaded {len(df)} rows to {args.table}")
        print(f"\nData summary:")
        print(f"  Total population: {df['POP'].sum():,.0f}")
        print(f"  Block groups: {len(df)}")
        print(f"  County: St. Louis County (FIPS 189)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
