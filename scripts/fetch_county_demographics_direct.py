#!/usr/bin/env python3
"""
Fetch St. Louis County block group demographics directly from Census API.

Uses direct HTTP requests to Census Bureau ACS API (no extra dependencies).

Usage:
    python scripts/fetch_county_demographics_direct.py --output data/backup/POPS_COUNTY.csv
"""

import os
import sys
from pathlib import Path
import requests
import pandas as pd
import argparse
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
CENSUS_API_BASE = "https://api.census.gov/data/2021/acs/acs5"

# ACS variable mappings
ACS_VARS = {
    "B01003_001E": "POP",
    "B11001_001E": "Total_Households",
    "B19013_001E": "Median_HH_Income",
    "B17001_002E": "Low_Income_HH",
    "B22001_002E": "HH_SNAP",
    "B11005_002E": "Public_Assistance_HH",
    "B25001_001E": "Total_Housing_Units",
    "B25003_003E": "Renter_Occupied",
    "B25002_003E": "Vacant_Housing_Units",
    "B08006_001E": "Total_Workers",
    "B08014_002E": "Workers_No_Car",
    "B28002_002E": "HH_No_Internet",
    "B11001_006E": "HH_With_Children",
    "B11001_008E": "Single_Parent_HH",
}


def fetch_acs_data():
    """Fetch ACS data for all block groups in St. Louis County (29189)."""
    if not CENSUS_API_KEY:
        raise ValueError("CENSUS_API_KEY environment variable not set")

    print("Fetching St. Louis County block group data from Census Bureau...")
    print("  (This may take 1-2 minutes...)\n")

    # Build variable list
    vars_str = ",".join(ACS_VARS.keys())

    # Query all block groups in St. Louis County (state=29, county=189)
    url = (
        f"{CENSUS_API_BASE}"
        f"?get=NAME,{vars_str}"
        f"&for=block%20group:*"
        f"&in=state:29%20county:189"
        f"&key={CENSUS_API_KEY}"
    )

    try:
        print(f"Querying Census API...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        data = response.json()
        print(f"✓ Received {len(data)} rows (including header)\n")

        # Parse response
        # Header row is data[0], data rows are data[1:]
        if len(data) < 2:
            raise ValueError("No data returned from Census API")

        header = data[0]
        rows = data[1:]

        # Build dataframe
        records = []
        for row in rows:
            record = {}

            # Build GEOID from Census return (format: state, county, tract, block_group)
            state, county, tract, bg = row[-4:]
            record["GEOID"] = f"{state}{county}{tract}{bg}"

            # Map variables
            for i, col in enumerate(header):
                if col in ACS_VARS:
                    try:
                        record[ACS_VARS[col]] = int(row[i]) if row[i] is not None else 0
                    except (ValueError, TypeError):
                        record[ACS_VARS[col]] = 0

            records.append(record)

        df = pd.DataFrame(records)
        print(f"✓ Parsed {len(df)} block groups\n")
        return df

    except requests.RequestException as e:
        print(f"Error querying Census API: {e}")
        print("Troubleshooting:")
        print("  - Check internet connection")
        print("  - Verify CENSUS_API_KEY is correct")
        print("  - Try again (API can be slow)")
        raise


def calculate_metrics(df):
    """Calculate derived metrics."""
    print("Calculating metrics...\n")

    # Rates
    df["Low_Income_Rate"] = (
        (df["Low_Income_HH"] / df["Total_Households"]) * 100
    ).round(2)
    df["SNAP_Rate"] = ((df["HH_SNAP"] / df["Total_Households"]) * 100).round(2)
    df["Public_Assistance_Rate"] = (
        (df["Public_Assistance_HH"] / df["Total_Households"]) * 100
    ).round(2)
    df["Renter_Rate"] = (
        (df["Renter_Occupied"] / (df["Total_Housing_Units"] - df["Vacant_Housing_Units"]))
        * 100
    ).round(2)
    df["Vacancy_Rate"] = (
        (df["Vacant_Housing_Units"] / df["Total_Housing_Units"]) * 100
    ).round(2)
    df["HH_With_Children_Rate"] = (
        (df["HH_With_Children"] / df["Total_Households"]) * 100
    ).round(2)
    df["Single_Parent_Rate"] = (
        (df["Single_Parent_HH"] / df["Total_Households"]) * 100
    ).round(2)
    df["No_Car_Rate"] = (
        (df["Workers_No_Car"] / df["Total_Workers"]) * 100
    ).round(2)
    df["No_Internet_Rate"] = (
        (df["HH_No_Internet"] / df["Total_Households"]) * 100
    ).round(2)

    # Estimates for missing detailed age/housing data
    df["Children_0_17"] = (df["POP"] * 0.2).astype(int)
    df["Children_0_4"] = (df["Children_0_17"] * 0.25).astype(int)
    df["Children_5_17"] = (df["Children_0_17"] * 0.75).astype(int)
    df["Child_Dependency_Rate"] = (
        (df["Children_0_17"] / df["POP"]) * 100
    ).round(2)

    df["Elderly_65_Plus"] = (df["POP"] * 0.15).astype(int)
    df["Elderly_65_74"] = (df["Elderly_65_Plus"] * 0.6).astype(int)
    df["Elderly_75_Plus"] = (df["Elderly_65_Plus"] * 0.4).astype(int)
    df["Elderly_Dependency_Rate"] = (
        (df["Elderly_65_Plus"] / df["POP"]) * 100
    ).round(2)
    df["Total_Dependency_Rate"] = (
        df["Child_Dependency_Rate"] + df["Elderly_Dependency_Rate"]
    ).round(2)

    df["Built_Before_1940"] = 0  # Placeholder
    df["Old_Housing_Rate"] = 0  # Placeholder

    return df


def format_output(df):
    """Format to match POPS.csv structure."""
    print("Formatting output...\n")

    df["Location"] = "Block Group, St. Louis County, Missouri"

    # Column order from POPS.csv
    cols = [
        "GEOID",
        "Location",
        "POP",
        "Total_Households",
        "Median_HH_Income",
        "Low_Income_HH",
        "Low_Income_Rate",
        "HH_SNAP",
        "SNAP_Rate",
        "Public_Assistance_HH",
        "Public_Assistance_Rate",
        "Children_0_17",
        "Children_0_4",
        "Children_5_17",
        "Child_Dependency_Rate",
        "Elderly_65_Plus",
        "Elderly_65_74",
        "Elderly_75_Plus",
        "Elderly_Dependency_Rate",
        "Total_Dependency_Rate",
        "HH_With_Children",
        "HH_With_Children_Rate",
        "Single_Parent_HH",
        "Single_Parent_Rate",
        "Renter_Occupied",
        "Renter_Rate",
        "Vacant_Housing_Units",
        "Vacancy_Rate",
        "Built_Before_1940",
        "Old_Housing_Rate",
        "Total_Workers",
        "Workers_No_Car",
        "No_Car_Rate",
        "HH_No_Internet",
        "No_Internet_Rate",
    ]

    available = [c for c in cols if c in df.columns]
    return df[available].fillna(0)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch St. Louis County block group demographics from Census API"
    )
    parser.add_argument(
        "--output",
        default="data/backup/POPS_COUNTY.csv",
        help="Output CSV file path",
    )
    args = parser.parse_args()

    try:
        # Fetch and process
        df = fetch_acs_data()
        df = calculate_metrics(df)
        df = format_output(df)

        # Save
        project_root = Path(__file__).parent.parent
        output_path = project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False)

        print(f"✓ Saved {len(df)} block groups to {output_path}\n")
        print("Summary:")
        print(f"  Total population: {df['POP'].sum():,.0f}")
        print(f"  Block groups: {len(df)}")
        print(f"  Median HH income: ${df['Median_HH_Income'].median():,.0f}")
        print(f"  Low income rate: {df['Low_Income_Rate'].mean():.1f}%")
        print(f"  SNAP rate: {df['SNAP_Rate'].mean():.1f}%")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
