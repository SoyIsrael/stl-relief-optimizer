# STL Site Optimizer

Civic site optimization tool for identifying optimal service locations across St. Louis City and County using census tract data and geospatial analysis.

## Overview

This project analyzes census tract demographics and candidate site locations to support data-driven decisions about where to place civic services, community centers, or other public resources in the St. Louis metropolitan area.

**Key Features:**

- Census tract boundary visualization with population data
- Candidate site generation and evaluation
- Interactive map output for stakeholder review
- Snowflake integration for scalable data storage

## Tech Stack

| Component     | Technology                    |
| ------------- | ----------------------------- |
| Language      | Python 3.10+                  |
| Geospatial    | GeoPandas, Shapely, Folium    |
| Data          | Pandas, Census Bureau ACS API |
| Database      | Snowflake                     |
| Visualization | Folium (interactive maps)     |

## Project Structure

```
stl-site-optimizer/
├── src/                      # Source code
│   ├── data_ingestion/       # Data loading (Census API, Snowflake, shapefiles)
│   ├── processing/           # Data processing (centroids, candidate generation)
│   └── visualization/        # Map building
├── scripts/                  # CLI entry points
│   ├── run_pipeline.py       # Main pipeline
│   └── upload_to_snowflake.py
├── data/raw/                 # Census shapefiles
├── outputs/                  # Generated maps
└── notebooks/                # Jupyter notebooks
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Snowflake

Copy `.env.example` to `.env` and fill in your Snowflake credentials:

```bash
cp .env.example .env
```

### 3. Upload Data to Snowflake (One-time)

```bash
# Upload block group boundaries
python scripts/upload_boundaries.py

# Upload block group demographics and vulnerability metrics
python scripts/upload_pops_data.py
```

### 4. Download Census Shapefiles (Optional)

Block group shapefiles are included in `data/raw/` for local development or as fallback:

- File: `tl_2020_29_bg.shp` (and associated .dbf, .shx, .prj files)
- Geographic scope: Missouri (covers St. Louis City FIPS 510 and St. Louis County FIPS 189)

## Usage

### Run the Pipeline

```bash
# Basic run (loads block groups and demographics from Snowflake)
python scripts/run_pipeline.py

# Generate 500 synthetic candidate sites
python scripts/run_pipeline.py --generate-candidates 500

# Use local shapefile instead of Snowflake
python scripts/run_pipeline.py --use-local-shapefile

# Custom output path
python scripts/run_pipeline.py --output outputs/my_map.html
```

### Using as a Library

```python
from src.data_ingestion import load_stl_tracts, SnowflakeClient
from src.processing import process_tracts, generate_candidates
from src.visualization import build_stl_map, save_map

# Load and process tracts
tracts = load_stl_tracts("data/raw/tl_2020_29_tract.shp")
tracts = process_tracts(tracts)

# Generate candidates
candidates = generate_candidates(n=100)

# Build map
m = build_stl_map(tracts, candidates)
save_map(m, "outputs/map.html")
```

## Data Sources

- **Census Tracts**: [TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) (2020)
- **Population Data**: [American Community Survey 5-Year Estimates](https://www.census.gov/programs-surveys/acs) via Census API
- **Geographic Scope**: St. Louis City (FIPS 510) and St. Louis County (FIPS 189), Missouri

## Team

- **Israel Chavez** - israel.chavez7272@gmail.com
- **Eric Wismar** - eric.wismar@gmail.com
- **Mahfud Bouad** - mahfoudbouad@gmail.com

## License
