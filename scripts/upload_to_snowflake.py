#!/usr/bin/env python3
"""
Upload local CSV data to Snowflake.

Usage:
    python scripts/upload_to_snowflake.py

This is a one-time utility to migrate existing CSV data to Snowflake.
Uploads:
- candidate_sites.csv -> CANDIDATE_SITES
- candidate_sites_big.csv -> CANDIDATE_SITES_BIG
- tract_info.csv -> TRACT_INFO
- demand_tracts.csv -> DEMAND_TRACTS
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import SnowflakeClient


def main():
    project_root = Path(__file__).parent.parent

    # CSV files to upload
    csv_files = {
        "candidate_sites.csv": "CANDIDATE_SITES",
        "candidate_sites_big.csv": "CANDIDATE_SITES_BIG",
        "tract_info.csv": "TRACT_INFO",
        "demand_tracts.csv": "DEMAND_TRACTS",
    }

    print("Connecting to Snowflake...")
    client = SnowflakeClient()

    for csv_name, table_name in csv_files.items():
        csv_path = project_root / csv_name
        if not csv_path.exists():
            # Also check in data/ directory
            csv_path = project_root / "data" / csv_name

        if not csv_path.exists():
            print(f"  Skipping {csv_name} (file not found)")
            continue

        print(f"Uploading {csv_name} -> {table_name}...")
        df = pd.read_csv(csv_path)
        client.write_table(df, table_name)
        print(f"  Uploaded {len(df)} rows")

    print("\nDone! Data is now in Snowflake.")


if __name__ == "__main__":
    main()
