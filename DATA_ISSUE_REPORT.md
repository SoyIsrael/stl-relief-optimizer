# Data Coverage Issue Report

## Summary
The missing population data you're seeing is because **Mahfud's CSV demographic data only covers St. Louis City (FIPS 510), not St. Louis County (FIPS 189)**.

## The Numbers
- **BLOCK_GROUP_BOUNDARIES**: 1,062 total block groups
  - St. Louis City (510): 314 block groups
  - St. Louis County (189): 748 block groups

- **BLOCK_GROUP_DEMOGRAPHICS**: 314 total block groups
  - St. Louis City (510): 314 block groups ✓
  - St. Louis County (189): 0 block groups ✗

## Why This Happened
When you run the streamlit app and perform a LEFT JOIN:
```sql
LEFT JOIN BLOCK_GROUP_DEMOGRAPHICS p ON b.GEOID = p.GEOID
COALESCE(p.POP::FLOAT, 0) AS POP  -- defaults to 0 if no match
```

The 748 County block groups don't find matches, so they get `POP = 0`.

## What We Have
- ✓ Full boundaries and visualization for entire St. Louis City + County
- ✓ Complete demographic data for **St. Louis City only** (314 block groups)
- ✗ No demographic data for St. Louis County (748 block groups)

## Options Going Forward

### Option 1: City-Only Analysis (Recommended for now)
- Filter the app to only show/analyze St. Louis City block groups
- Simplest approach, no data quality issues
- Use all 314 City block groups with complete data

### Option 2: Keep County as Context
- Keep County block groups visible on map (grayed out)
- Only allow optimization/selection in City
- Good for stakeholder context

### Option 3: Find County Data
- Reach out to Mahfud to see if County demographic data exists
- May be in a separate file or require different processing
- Would give complete coverage

## Recommendation
I'd suggest **Option 1** (City-only) for now, since the full demographic data is available for City. If County data becomes available later, it's easy to add.

Would you like me to update the streamlit app to:
1. Filter to City-only block groups
2. Add a notice explaining the data coverage
3. Keep County visible but disable for selection?
