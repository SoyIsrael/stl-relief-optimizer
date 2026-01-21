#!/usr/bin/env python3
"""
Upload block group demographics and vulnerability data to Snowflake.

Usage:
    python scripts/upload_pops_data.py

This script loads the block-group-level demographics data created by Mahfud
and uploads it to Snowflake for use in the optimizer pipeline.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import SnowflakeClient


def main():
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data" / "backup" / "POPS.csv"

    if not data_path.exists():
        print(f"Error: {data_path} not found")
        sys.exit(1)

    print(f"Loading {data_path}...")
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df)} block groups")

    # Ensure GEOID is string type for consistency
    df["GEOID"] = df["GEOID"].astype(str)

    print("Connecting to Snowflake...")
    client = SnowflakeClient()

    print("Uploading to BLOCK_GROUP_DEMOGRAPHICS table...")
    client.write_table(df, "BLOCK_GROUP_DEMOGRAPHICS", if_exists="replace")
    print(f"  Successfully uploaded {len(df)} rows to BLOCK_GROUP_DEMOGRAPHICS table")

    print("\nDone! Block group demographics data is now in Snowflake.")


if __name__ == "__main__":
    main()
