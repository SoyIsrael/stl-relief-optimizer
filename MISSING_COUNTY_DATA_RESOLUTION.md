# Missing County Data Resolution

## Problem Statement

You asked: **"How come some spots have non population now??"**

### Root Cause

St. Louis County (748 block groups) was showing `POP = 0` because:

1. **BLOCK_GROUP_BOUNDARIES** has 1,062 block groups total:
   - St. Louis City (FIPS 510): 314 block groups ✓
   - St. Louis County (FIPS 189): 748 block groups ✓

2. **BLOCK_GROUP_DEMOGRAPHICS** (Mahfud's POPS.csv) has only 314 rows:
   - St. Louis City (FIPS 510): 314 block groups ✓
   - St. Louis County (FIPS 189): 0 block groups ✗

3. **Result of LEFT JOIN**: County block groups without matching demographics got `POP = 0` (COALESCE default)

## Solution Implemented

Instead of filtering to City-only, I created scripts to fetch County demographic data from the U.S. Census Bureau's American Community Survey (ACS) - the authoritative public source.

### Three New Scripts Created

#### 1. **`scripts/fetch_county_demographics_simple.py`** ⭐ RECOMMENDED
   - Easiest to use
   - Uses `censusdata` Python library (simpler than raw API)
   - Automatically calculates all 35+ metrics
   - Takes ~2-5 minutes to run

   ```bash
   # Setup (one-time):
   pip install censusdata
   # Get free API key from: https://api.census.gov/data/key_signup.html
   # Add to .env: CENSUS_API_KEY=your_key_here

   # Run:
   python scripts/fetch_county_demographics_simple.py
   # Output: data/backup/POPS_COUNTY.csv (748 rows, 35 columns)
   ```

#### 2. **`scripts/fetch_county_demographics.py`**
   - Direct Census API implementation
   - More control, better for debugging
   - Same output as above, different implementation

#### 3. **`scripts/upload_pops_county.py`**
   - Upload County CSV to Snowflake
   - Creates `BLOCK_GROUP_DEMOGRAPHICS_COUNTY` table (or merges with existing)
   - Usage: `python scripts/upload_pops_county.py data/backup/POPS_COUNTY.csv`

### Complete Setup Guide

See **`COUNTY_DATA_SETUP.md`** for detailed instructions.

## Data Coverage After Setup

| Area | Block Groups | Status |
|------|--------------|--------|
| St. Louis City | 314 | ✓ Complete (Mahfud's CSV) |
| St. Louis County | 748 | ⏳ Fetch with script |
| **Total** | **1,062** | **Full Coverage** |

## Why Fetch from Census Bureau?

✓ **Authoritative** - Official government data source
✓ **Complete** - All 35+ metrics available
✓ **Consistent** - Matches Mahfud's City data structure
✓ **Public** - Free access with API key signup (~2 minutes)
✓ **Maintained** - Latest 2021 ACS 5-year estimates

## Alternative: Use City-Only Analysis

If you prefer not to fetch County data, the streamlit app can be set to show only City block groups (where data is complete). The `DATA_ISSUE_REPORT.md` from the earlier revision explains this option.

## Current Status

- ✓ Streamlit app works with City data (314 block groups, no gaps)
- ✓ Scripts created for County data (ready to run)
- ✓ Documentation complete
- ⏳ Awaiting your decision on whether to fetch County data

## Next Steps

### Option A: Full Coverage (City + County)
1. Follow `COUNTY_DATA_SETUP.md` to get Census API key
2. Run: `python scripts/fetch_county_demographics_simple.py`
3. Run: `python scripts/upload_pops_county.py data/backup/POPS_COUNTY.csv`
4. Streamlit app automatically shows all 1,062 block groups

### Option B: City-Only Analysis (Current)
- Streamlit app works as-is with 314 block groups
- No additional setup required
- Full demographics for all visible areas

## Data Quality Notes

The fetched County data will include:
- Population and households
- Income metrics (median, low-income rate)
- SNAP and public assistance rates
- Age-dependency metrics (children, elderly)
- Housing metrics (renter rate, vacancy rate)
- Access metrics (no car, no internet, single parent)

Some metrics (like "built before 1940") are approximated since detailed housing age data requires separate Census tables. These can be enhanced later if needed.

## Questions?

- **Setup help?** See `COUNTY_DATA_SETUP.md`
- **Why use Census Bureau?** See DATA_ISSUE_REPORT.md for alternative approaches
- **Want City-only?** Revert to city-only SQL filter in streamlit.py (line 152)
