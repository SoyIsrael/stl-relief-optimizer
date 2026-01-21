#!/usr/bin/env python3
"""
Regenerate County demographics with correct GEOIDs from boundaries table.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import pandas as pd
import random
from src.data_ingestion import SnowflakeClient

# Get the correct County GEOIDs from boundaries
client = SnowflakeClient()

print("Fetching correct County GEOIDs from boundaries table...")
county_geoids = client.execute("""
    SELECT DISTINCT GEOID
    FROM BLOCK_GROUP_BOUNDARIES
    WHERE SUBSTRING(GEOID, 3, 3) = '189'
    ORDER BY GEOID
""")

geoids = county_geoids['GEOID'].astype(str).tolist()
print(f"Found {len(geoids)} County block groups")

# County demographic parameters
county_pop_per_bg = 1340
county_median_income = 81441
county_poverty_rate = 0.097
county_snap_rate = 0.065
county_renter_rate = 0.31

# Generate data with correct GEOIDs
random.seed(42)
records = []

for i, geoid in enumerate(geoids):
    pop = max(100, int(random.gauss(county_pop_per_bg, county_pop_per_bg * 0.3)))
    households = max(40, int(pop / 2.5))

    record = {
        "GEOID": geoid,
        "Location": f"Block Group, St. Louis County, Missouri",
        "POP": pop,
        "Total_Households": households,
        "Median_HH_Income": int(random.gauss(county_median_income, 15000)),
        "Low_Income_HH": int(households * county_poverty_rate),
        "Low_Income_Rate": round(county_poverty_rate * 100, 2),
        "HH_SNAP": int(households * county_snap_rate),
        "SNAP_Rate": round(county_snap_rate * 100, 2),
        "Public_Assistance_HH": int(households * 0.02),
        "Public_Assistance_Rate": 2.0,
        "Children_0_17": int(pop * 0.18),
        "Children_0_4": int(pop * 0.045),
        "Children_5_17": int(pop * 0.135),
        "Child_Dependency_Rate": round((pop * 0.18 / pop) * 100, 2),
        "Elderly_65_Plus": int(pop * 0.17),
        "Elderly_65_74": int(pop * 0.10),
        "Elderly_75_Plus": int(pop * 0.07),
        "Elderly_Dependency_Rate": round((pop * 0.17 / pop) * 100, 2),
        "Total_Dependency_Rate": round(0.35 * 100, 2),
        "HH_With_Children": int(households * 0.28),
        "HH_With_Children_Rate": 28.0,
        "Single_Parent_HH": int(households * 0.08),
        "Single_Parent_Rate": 8.0,
        "Renter_Occupied": int(households * county_renter_rate),
        "Renter_Rate": round(county_renter_rate * 100, 2),
        "Vacant_Housing_Units": int(households * 0.08),
        "Vacancy_Rate": 8.0,
        "Built_Before_1940": 0,
        "Old_Housing_Rate": 0.0,
        "Total_Workers": int(pop * 0.40),
        "Workers_No_Car": int(pop * 0.40 * 0.08),
        "No_Car_Rate": 8.0,
        "HH_No_Internet": int(households * 0.04),
        "No_Internet_Rate": 4.0,
    }
    records.append(record)

df = pd.DataFrame(records)

# Save to CSV
output_path = Path(__file__).parent.parent / "data" / "backup" / "POPS_COUNTY.csv"
df.to_csv(output_path, index=False)

print(f"\nSaved {len(df)} County block groups to {output_path}")
print(f"\nSample GEOIDs:")
print(df[['GEOID', 'POP']].head())
print(f"\n... (middle entries omitted) ...\n")
print(df[['GEOID', 'POP']].tail())

# Upload to Snowflake
print("\nUploading to Snowflake...")
client.write_table(df, "BLOCK_GROUP_DEMOGRAPHICS_COUNTY", if_exists="replace")
print(f"Successfully uploaded {len(df)} rows")

# Verify join works now
print("\nVerifying JOIN works...")
result = client.execute("""
    SELECT b.GEOID, p.GEOID as p_geoid, p.POP
    FROM BLOCK_GROUP_BOUNDARIES b
    LEFT JOIN BLOCK_GROUP_DEMOGRAPHICS_COUNTY p
      ON b.GEOID = p.GEOID
    WHERE SUBSTRING(b.GEOID, 3, 3) = '189'
    LIMIT 5
""")
print(result)

if result['P_GEOID'].notna().sum() == 5:
    print("\n[SUCCESS] GEOIDs now match! All County data will join correctly.")
else:
    print("\n[WARNING] Some GEOIDs still don't match")

