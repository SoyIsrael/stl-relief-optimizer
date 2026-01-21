#!/usr/bin/env python3
"""
Clean up legacy tables in Snowflake.

Usage:
    python scripts/cleanup_snowflake.py

This removes old/duplicate tables from development iterations.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import SnowflakeClient


def main():
    tables_to_drop = ["POPS", "POPS2", "BOUNDARIES", "BOUNDARIES2"]

    print("Connecting to Snowflake...")
    client = SnowflakeClient()

    for table in tables_to_drop:
        print(f"Dropping {table}...")
        try:
            client.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  [OK] Dropped {table}")
        except Exception as e:
            print(f"  [ERROR] Error dropping {table}: {e}")

    print("\nCleanup complete! Kept: BLOCK_GROUP_DEMOGRAPHICS, CANDIDATE_SITES")


if __name__ == "__main__":
    main()
