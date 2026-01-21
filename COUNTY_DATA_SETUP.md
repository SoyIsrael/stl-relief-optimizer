# St. Louis County Demographic Data Setup

To add St. Louis County block group demographics to complement the City data, you have two options:

## Option 1: Automatic Fetch from Census Bureau (Recommended)

This approach fetches data directly from the U.S. Census Bureau's ACS 5-year estimates.

### Setup Steps

1. **Get Census API Key** (free, takes 2 minutes)
   - Visit: https://api.census.gov/data/key_signup.html
   - Fill out the form and submit
   - Check your email for the API key

2. **Install Dependencies**
   ```bash
   pip install censusdata requests
   ```

3. **Set API Key**
   - Add to `.env` file in project root:
     ```
     CENSUS_API_KEY=your_key_here
     ```
   - OR set environment variable:
     ```bash
     export CENSUS_API_KEY="your_key_here"
     ```

4. **Run the Script**
   ```bash
   python scripts/fetch_county_demographics_simple.py
   # Output: data/backup/POPS_COUNTY.csv
   ```

### What This Does

- Fetches 2021 ACS 5-year data for all 748 St. Louis County block groups
- Calculates 35+ demographic metrics matching Mahfud's City data structure
- Outputs to `data/backup/POPS_COUNTY.csv`
- Takes ~2-5 minutes to run

### Available Scripts

Two scripts are provided with different complexity levels:

1. **`fetch_county_demographics_simple.py`** (Easiest)
   - Uses `censusdata` Python library (simpler abstraction)
   - Recommended for most users
   - Works with basic Census API key

2. **`fetch_county_demographics.py`** (More Control)
   - Direct Census API calls with custom chunking
   - More flexible for debugging/customization
   - Lower-level implementation

## Option 2: Download Pre-Processed Data

If you prefer not to set up Census API access:

**Coming Soon:** Pre-processed County data file (if available from project resources)

## Data Coverage After Setup

Once County data is fetched and uploaded to Snowflake:

| Area | Block Groups | Status |
|------|--------------|--------|
| St. Louis City | 314 | ✓ Complete |
| St. Louis County | 748 | ✓ Complete (after setup) |
| **Total** | **1,062** | **Ready for Full Analysis** |

## Next Steps After Fetching County Data

1. **Upload to Snowflake**
   ```bash
   python scripts/upload_pops_county.py data/backup/POPS_COUNTY.csv
   ```

2. **Update Streamlit App** (optional)
   - Revert the City-only filter in `archive/streamlit.py`
   - App will then show both City + County data

3. **Verify Data**
   ```bash
   python scripts/diagnose_data.py
   ```

## Troubleshooting

**"ModuleNotFoundError: No module named 'censusdata'"**
```bash
pip install censusdata
```

**"Missing Snowflake credentials: CENSUS_API_KEY"**
- Verify API key is set in `.env` or environment variable
- Check https://api.census.gov/data/key_signup.html for new key

**Script runs but hangs or times out**
- Census API can be slow with many geography requests
- Check internet connection
- Try running during off-peak hours (early morning EST)

**Data looks wrong or incomplete**
- Run `python scripts/diagnose_data.py` to check
- Verify all 748 block groups were fetched
- Check for missing or NULL values in key columns

## Data Metrics Included

County demographic data will include:

**Economic:**
- Median Household Income
- Low Income Rate (% below poverty)
- SNAP participation rate
- Public Assistance rate

**Age/Dependency:**
- Child Dependency Rate
- Elderly Dependency Rate
- Total Dependency Rate

**Housing:**
- Renter rate
- Vacancy rate
- Housing age estimate

**Access:**
- No vehicle rate
- No internet rate
- Single parent household rate

## References

- [Census Bureau ACS Data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [Census Reporter](https://censusreporter.org/)
- [Missouri Census Data Center](https://mcdc.missouri.edu/)
- [censusdata Python Library](https://github.com/jtclaypool/censusdata)
