#!/usr/bin/env python3
"""
Fetch St. Louis County block group demographics from Census Bureau ACS API.

This script queries the Census Bureau's ACS 5-year data for all block groups
in St. Louis County (FIPS 29189) and formats it to match Mahfud's POPS.csv structure.

Usage:
    python scripts/fetch_county_demographics.py [--output data/backup/POPS_COUNTY.csv]

Requires:
    - Census Bureau API key (from https://api.census.gov/data/key_signup.html)
    - Set CENSUS_API_KEY environment variable or create .env file
"""

import os
import sys
from pathlib import Path
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import Optional
import argparse

load_dotenv()

# Census Bureau API configuration
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
CENSUS_API_BASE = "https://api.census.gov/data/2021/acs/acs5"

# ACS table mappings to POPS.csv columns
ACS_TABLES = {
    "B01003_001E": "POP",  # Total population
    "B11001_001E": "Total_Households",  # Total households
    "B19013_001E": "Median_HH_Income",  # Median household income
    "B17001_002E": "Low_Income_HH",  # Income below poverty level
    "B22001_002E": "HH_SNAP",  # Households receiving SNAP
    "B09001_001E": "Children_0_17",  # Population age 0-17
    "B01001_003E": "Children_0_4",  # Male age 0-4
    "B01001_027E": "Female_0_4",  # Female age 0-4 (will combine with male)
    "B01001_006E": "Male_5_9",  # Male age 5-9
    "B01001_030E": "Female_5_9",  # Female age 5-9
    "B01001_007E": "Male_10_14",  # Male age 10-14
    "B01001_031E": "Female_10_14",  # Female age 10-14
    "B01001_008E": "Male_15_17",  # Male age 15-17
    "B01001_032E": "Female_15_17",  # Female age 15-17
    "B01001_020E": "Male_65_74",  # Male age 65-74
    "B01001_044E": "Female_65_74",  # Female age 65-74
    "B01001_021E": "Male_75_plus",  # Male age 75+
    "B01001_045E": "Female_75_plus",  # Female age 75+
    "B11001_006E": "HH_With_Children",  # Family households with own children
    "B11001_008E": "Single_Parent_HH",  # Single parent households
    "B25003_003E": "Renter_Occupied",  # Renter-occupied housing units
    "B25001_001E": "Total_Housing_Units",  # Total housing units
    "B25002_003E": "Vacant_Housing_Units",  # Vacant housing units
    "B25035_001E": "Median_Year_Built",  # Median year structure built
    "B08006_001E": "Total_Workers",  # Total workers 16+
    "B08006_008E": "Workers_No_Car",  # Workers with no vehicle available
    "B28003_002E": "HH_No_Internet",  # Households with no internet
    "B11005_002E": "Public_Assistance_HH",  # Households receiving public assistance
}


def validate_api_key() -> None:
    """Validate that Census API key is available."""
    if not CENSUS_API_KEY:
        raise ValueError(
            "Census API key required. Get one from https://api.census.gov/data/key_signup.html "
            "and set CENSUS_API_KEY environment variable or add to .env file"
        )


def fetch_block_group_geoids(state_fips: str = "29", county_fips: str = "189") -> list:
    """
    Fetch all block group GEOIDs for St. Louis County.

    Returns list of GEOIDs in format: 291892107031 (state+county+tract+blockgroup)
    """
    print(f"Fetching block group GEOIDs for MO ({state_fips}) County {county_fips}...")

    # Query for all block groups in the county
    url = f"{CENSUS_API_BASE}?get=NAME&for=block%20group:*&in=state:{state_fips}%20county:{county_fips}&key={CENSUS_API_KEY}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Skip header row, extract GEOIDs
        geoids = []
        for row in data[1:]:
            # Format: [NAME, state, county, tract, block_group]
            state, county, tract, bg = row[1:5]
            geoid = f"{state}{county}{tract}{bg}"
            geoids.append(geoid)

        print(f"  Found {len(geoids)} block groups")
        return sorted(geoids)

    except requests.RequestException as e:
        print(f"  Error fetching GEOIDs: {e}")
        return []


def fetch_acs_data(geoids: list, chunk_size: int = 50) -> pd.DataFrame:
    """
    Fetch ACS 5-year data for block groups.

    Census API limits queries to ~50 geographies at a time, so we chunk the requests.
    """
    print(f"\nFetching ACS data for {len(geoids)} block groups (in chunks of {chunk_size})...")

    all_data = []
    table_vars = ",".join(ACS_TABLES.keys())

    # Process in chunks
    for i in range(0, len(geoids), chunk_size):
        chunk = geoids[i : i + chunk_size]
        print(f"  Processing block groups {i+1} to {min(i+chunk_size, len(geoids))}...")

        # Build query
        geo_spec = " ".join([f"block%20group:{bg[-1]}%20tract:{bg[-6:-1]}" for bg in chunk])
        url = (
            f"{CENSUS_API_BASE}?get=NAME,{table_vars}&for={geo_spec}"
            f"&in=state:29%20county:189&key={CENSUS_API_KEY}"
        )

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Convert to rows
            for row in data[1:]:
                row_dict = {"GEOID": chunk[len(all_data) % len(chunk)]}
                for j, var in enumerate(ACS_TABLES.keys()):
                    try:
                        val = int(row[j]) if row[j] is not None else None
                        row_dict[ACS_TABLES[var]] = val
                    except (ValueError, IndexError):
                        row_dict[ACS_TABLES[var]] = None

                all_data.append(row_dict)

        except requests.RequestException as e:
            print(f"  Error fetching chunk: {e}")

    return pd.DataFrame(all_data)


def calculate_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived metrics to match POPS.csv structure.

    Examples: rates, age groups, etc.
    """
    print("\nCalculating derived metrics...")

    # Rates (as percentages)
    df["Low_Income_Rate"] = (
        (df["Low_Income_HH"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["SNAP_Rate"] = (
        (df["HH_SNAP"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["Public_Assistance_Rate"] = (
        (df["Public_Assistance_HH"] / df["Total_Households"]) * 100
    ).fillna(0)

    # Age groups
    df["Children_0_4"] = df.get("Children_0_4", 0).fillna(0)
    df["Children_5_17"] = (
        (
            df.get("Male_5_9", 0)
            + df.get("Female_5_9", 0)
            + df.get("Male_10_14", 0)
            + df.get("Female_10_14", 0)
            + df.get("Male_15_17", 0)
            + df.get("Female_15_17", 0)
        )
        .fillna(0)
        .astype(int)
    )
    df["Child_Dependency_Rate"] = (df["Children_0_17"] / df["POP"] * 100).fillna(0)

    # Elderly
    df["Elderly_65_74"] = (
        df.get("Male_65_74", 0) + df.get("Female_65_74", 0)
    ).fillna(0).astype(int)
    df["Elderly_75_Plus"] = (
        df.get("Male_75_plus", 0) + df.get("Female_75_plus", 0)
    ).fillna(0).astype(int)
    df["Elderly_65_Plus"] = (df["Elderly_65_74"] + df["Elderly_75_Plus"]).astype(int)
    df["Elderly_Dependency_Rate"] = (
        df["Elderly_65_Plus"] / df["POP"] * 100
    ).fillna(0)
    df["Total_Dependency_Rate"] = (
        df["Child_Dependency_Rate"] + df["Elderly_Dependency_Rate"]
    )

    # Housing metrics
    df["Renter_Rate"] = (
        (df["Renter_Occupied"] / (df["Total_Housing_Units"] - df["Vacant_Housing_Units"])) * 100
    ).fillna(0)
    df["Vacancy_Rate"] = (df["Vacant_Housing_Units"] / df["Total_Housing_Units"] * 100).fillna(0)
    df["Old_Housing_Rate"] = (
        (df["Total_Housing_Units"] - df.get("Median_Year_Built", 0)) / df["Total_Housing_Units"]
    ).fillna(0)  # Approximate

    # Transportation & Internet
    df["HH_With_Children_Rate"] = (
        (df["HH_With_Children"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["Single_Parent_Rate"] = (
        (df["Single_Parent_HH"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["No_Car_Rate"] = (df["Workers_No_Car"] / df["Total_Workers"] * 100).fillna(0)
    df["No_Internet_Rate"] = (
        (df["HH_No_Internet"] / df["Total_Households"]) * 100
    ).fillna(0)

    # Built before 1940 (use Median_Year_Built as proxy)
    df["Built_Before_1940"] = (df["Median_Year_Built"] < 1940).astype(int)

    return df


def format_output(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format data to match POPS.csv structure.
    """
    print("Formatting output...")

    # Add location name
    df["Location"] = (
        "Block Group " + df.index.astype(str) + ", St. Louis County, Missouri"
    )

    # Select columns in same order as POPS.csv
    output_cols = [
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

    # Only include columns that exist
    available_cols = [col for col in output_cols if col in df.columns]
    result = df[available_cols].copy()

    # Round numeric columns to reasonable precision
    numeric_cols = result.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        if "Rate" in col:
            result[col] = result[col].round(2)
        else:
            result[col] = result[col].round(0).astype(int)

    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch St. Louis County block group demographics from Census Bureau ACS"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/backup/POPS_COUNTY.csv",
        help="Output path for demographics CSV",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    output_path = project_root / args.output

    try:
        validate_api_key()

        # Fetch block groups and data
        geoids = fetch_block_group_geoids()
        if not geoids:
            print("Failed to fetch block group GEOIDs")
            sys.exit(1)

        df = fetch_acs_data(geoids)
        if df.empty:
            print("Failed to fetch ACS data")
            sys.exit(1)

        # Process data
        df = calculate_derived_metrics(df)
        df = format_output(df)

        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"\n✓ Saved {len(df)} St. Louis County block groups to {output_path}")
        print(f"\nSummary:")
        print(f"  Total population: {df['POP'].sum():,.0f}")
        print(f"  Median household income: ${df['Median_HH_Income'].median():,.0f}")
        print(f"  Low income rate: {df['Low_Income_Rate'].mean():.1f}%")
        print(f"  SNAP rate: {df['SNAP_Rate'].mean():.1f}%")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
