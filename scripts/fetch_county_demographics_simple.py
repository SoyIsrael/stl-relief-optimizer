#!/usr/bin/env python3
"""
Fetch St. Louis County block group demographics using censusdata library.

This is a simpler alternative using the censusdata Python package.

Installation:
    pip install censusdata

Setup:
    Get API key from https://api.census.gov/data/key_signup.html
    Set environment variable: export CENSUS_API_KEY="your_key_here"

Usage:
    python scripts/fetch_county_demographics_simple.py --output data/backup/POPS_COUNTY.csv
"""

import os
import sys
from pathlib import Path
import pandas as pd
import argparse
from dotenv import load_dotenv

load_dotenv()

try:
    import censusdata
except ImportError:
    print("Error: censusdata library not installed")
    print("Install with: pip install censusdata")
    sys.exit(1)

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")


def get_county_block_groups():
    """
    Fetch St. Louis County block group demographic data using censusdata.

    Uses ACS 5-year 2021 data (most recent complete dataset).
    St. Louis County FIPS: 29189
    """
    if not CENSUS_API_KEY:
        raise ValueError(
            "Census API key required. Get one from https://api.census.gov/data/key_signup.html "
            "and set CENSUS_API_KEY environment variable"
        )

    print("Fetching St. Louis County block group demographics...")
    print("  (This may take a moment...)\n")

    # Define the variables we want to pull from ACS
    # Format: {census_var: display_name}
    variables = {
        "B01003_001E": "POP",  # Total population
        "B11001_001E": "Total_Households",
        "B19013_001E": "Median_HH_Income",
        "B17001_002E": "Below_Poverty_Level",
        "B22001_002E": "SNAP_Participants",
        "B11005_002E": "Public_Assistance",
        "B01001_026E": "Pop_65_Plus",  # Age 65 and over total
        "B11001_006E": "Families_With_Children",
        "B11001_008E": "Single_Parent_Families",
        "B25003_003E": "Renter_Occupied",
        "B25002_001E": "Total_Housing_Units",
        "B25002_003E": "Vacant_Housing_Units",
        "B08006_001E": "Workers_16_Plus",
        "B08014_002E": "Workers_No_Vehicle",
        "B28002_002E": "No_Internet_Access",
        "B01001_002E": "Male_Pop",  # For age breakdowns
        "B01001_026E": "Female_65_Plus",
    }

    try:
        # Fetch data for all block groups in St. Louis County (29189)
        # State 29 = Missouri, County 189 = St. Louis County
        data = censusdata.download(
            "acs5",
            2021,
            censusdata.cenpy.states.MO.county.SLCO,  # St. Louis County
            censusdata.cenpy.ALL,  # All block groups
            variables,
            key=CENSUS_API_KEY,
        )

        print(f"✓ Successfully fetched {len(data)} block groups\n")
        return data

    except Exception as e:
        print(f"Error fetching data: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Verify CENSUS_API_KEY is set correctly")
        print("  2. Check internet connection")
        print("  3. Visit https://api.census.gov/data/key_signup.html to get/verify API key")
        raise


def calculate_metrics(df):
    """Calculate derived metrics to match POPS.csv structure."""
    print("Calculating derived metrics...\n")

    # Convert to numeric, handling any non-numeric values
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Rename columns to match POPS structure
    df = df.rename(
        columns={
            "Below_Poverty_Level": "Low_Income_HH",
            "SNAP_Participants": "HH_SNAP",
            "Public_Assistance": "Public_Assistance_HH",
            "Families_With_Children": "HH_With_Children",
            "Single_Parent_Families": "Single_Parent_HH",
            "Workers_No_Vehicle": "Workers_No_Car",
            "No_Internet_Access": "HH_No_Internet",
        }
    )

    # Calculate rates
    df["Low_Income_Rate"] = (
        (df["Low_Income_HH"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["SNAP_Rate"] = ((df["HH_SNAP"] / df["Total_Households"]) * 100).fillna(0)
    df["Public_Assistance_Rate"] = (
        (df["Public_Assistance_HH"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["Renter_Rate"] = (
        (df["Renter_Occupied"] / (df["Total_Housing_Units"] - df["Vacant_Housing_Units"]))
        * 100
    ).fillna(0)
    df["Vacancy_Rate"] = (
        (df["Vacant_Housing_Units"] / df["Total_Housing_Units"]) * 100
    ).fillna(0)
    df["HH_With_Children_Rate"] = (
        (df["HH_With_Children"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["Single_Parent_Rate"] = (
        (df["Single_Parent_HH"] / df["Total_Households"]) * 100
    ).fillna(0)
    df["No_Car_Rate"] = ((df["Workers_No_Car"] / df["Workers_16_Plus"]) * 100).fillna(0)
    df["No_Internet_Rate"] = (
        (df["HH_No_Internet"] / df["Total_Households"]) * 100
    ).fillna(0)

    # Age groups (approximations without detailed breakdowns)
    df["Elderly_65_Plus"] = df["Pop_65_Plus"]
    df["Elderly_Dependency_Rate"] = (df["Pop_65_Plus"] / df["POP"] * 100).fillna(0)

    # Estimate children (rough estimate)
    df["Children_0_17"] = (df["POP"] * 0.2).astype(int)  # Rough estimate ~20%
    df["Children_0_4"] = (df["Children_0_17"] * 0.25).astype(int)  # ~25% of children
    df["Children_5_17"] = (df["Children_0_17"] * 0.75).astype(int)
    df["Child_Dependency_Rate"] = (
        (df["Children_0_17"] / df["POP"]) * 100
    ).fillna(0)
    df["Total_Dependency_Rate"] = (
        df["Child_Dependency_Rate"] + df["Elderly_Dependency_Rate"]
    )

    # Placeholder columns
    df["Elderly_65_74"] = (df["Elderly_65_Plus"] * 0.6).astype(int)
    df["Elderly_75_Plus"] = (df["Elderly_65_Plus"] * 0.4).astype(int)
    df["Built_Before_1940"] = 0  # Not available from basic ACS
    df["Old_Housing_Rate"] = 0  # Not available without detailed housing age data
    df["Total_Workers"] = df["Workers_16_Plus"]
    df["Renter_Occupied"] = df["Renter_Occupied"]  # Already have this

    return df


def format_output(df):
    """Format data to match POPS.csv structure."""
    print("Formatting output...\n")

    # Add GEOID and Location from index
    df = df.reset_index()
    df["GEOID"] = df.index.map(lambda x: x[-1]) if hasattr(df.index, "__iter__") else ""
    df["Location"] = "Block Group, St. Louis County, Missouri"

    # Select and order columns to match POPS.csv
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

    available_cols = [col for col in output_cols if col in df.columns]
    result = df[available_cols].copy()

    # Round numeric columns
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
        # Fetch and process data
        df = get_county_block_groups()
        df = calculate_metrics(df)
        df = format_output(df)

        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"✓ Saved {len(df)} St. Louis County block groups to {output_path}\n")
        print(f"Summary:")
        print(f"  Total population: {df['POP'].sum():,.0f}")
        print(f"  Median household income: ${df['Median_HH_Income'].median():,.0f}")
        print(f"  Low income rate: {df['Low_Income_Rate'].mean():.1f}%")
        print(f"  SNAP rate: {df['SNAP_Rate'].mean():.1f}%")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
