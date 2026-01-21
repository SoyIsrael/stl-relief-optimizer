#!/usr/bin/env python3
"""
Diagnostic script to check data completeness in Snowflake tables.

This helps identify why some block groups have missing population data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion import SnowflakeClient


def diagnose():
    """Check data completeness across all tables."""
    client = SnowflakeClient()

    print("=" * 70)
    print("DATA COMPLETENESS DIAGNOSTIC")
    print("=" * 70)

    # Read all tables
    print("\n1. Reading BLOCK_GROUP_BOUNDARIES...")
    boundaries = client.get_boundaries()
    print(f"   - Rows: {len(boundaries)}")
    print(f"   - Columns: {list(boundaries.columns)}")
    print(f"   - Unique GEOIDs: {boundaries['GEOID'].nunique()}")
    print(f"   - GEOID type: {boundaries['GEOID'].dtype}")
    print(f"   - NULL GEOIDs: {boundaries['GEOID'].isna().sum()}")
    print(f"\n   Sample GEOIDs: {boundaries['GEOID'].head(3).tolist()}")

    print("\n2. Reading BLOCK_GROUP_DEMOGRAPHICS...")
    demographics = client.get_tract_info()
    print(f"   - Rows: {len(demographics)}")
    print(f"   - Columns: {list(demographics.columns)}")
    print(f"   - Unique GEOIDs: {demographics['GEOID'].nunique()}")
    print(f"   - GEOID type: {demographics['GEOID'].dtype}")
    print(f"   - NULL GEOIDs: {demographics['GEOID'].isna().sum()}")
    print(f"   - NULL POPs: {demographics.get('POP', demographics.get('pop', None)) is None}")

    if 'POP' in demographics.columns:
        pop_col = 'POP'
    elif 'pop' in demographics.columns:
        pop_col = 'pop'
    else:
        pop_col = None
        print("   - WARNING: No POP column found!")

    if pop_col:
        print(f"   - Rows with NULL {pop_col}: {demographics[pop_col].isna().sum()}")
        print(f"   - Rows with {pop_col} = 0: {(demographics[pop_col] == 0).sum()}")
        print(f"\n   Sample {pop_col} values: {demographics[pop_col].head(3).tolist()}")

    print(f"\n   Sample GEOIDs: {demographics['GEOID'].head(3).tolist()}")

    print("\n3. Checking JOIN alignment...")
    # Convert to string for comparison
    b_geoids = set(boundaries['GEOID'].astype(str))
    d_geoids = set(demographics['GEOID'].astype(str))

    only_in_boundaries = b_geoids - d_geoids
    only_in_demographics = d_geoids - b_geoids
    both = b_geoids & d_geoids

    print(f"   - GEOIDs only in BOUNDARIES: {len(only_in_boundaries)}")
    if only_in_boundaries:
        print(f"     Examples: {list(only_in_boundaries)[:5]}")

    print(f"   - GEOIDs only in DEMOGRAPHICS: {len(only_in_demographics)}")
    if only_in_demographics:
        print(f"     Examples: {list(only_in_demographics)[:5]}")

    print(f"   - GEOIDs in both tables: {len(both)}")

    # Check data types
    print("\n4. Data type comparison...")
    print(f"   - BOUNDARIES GEOID sample: {repr(boundaries['GEOID'].iloc[0])}")
    print(f"   - DEMOGRAPHICS GEOID sample: {repr(demographics['GEOID'].iloc[0])}")

    print("\n" + "=" * 70)

    if len(only_in_boundaries) > 0:
        print("⚠️  ISSUE FOUND: Some block groups have no population data")
        print(f"   {len(only_in_boundaries)} block groups in BOUNDARIES lack DEMOGRAPHICS entries")
    else:
        print("✓ All block groups have matching demographic data")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    diagnose()
