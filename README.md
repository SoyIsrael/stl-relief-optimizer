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

### 2. Configure Snowflake (Optional)

Copy `.env.example` to `.env` and fill in your Snowflake credentials:

```bash
cp .env.example .env
```

### 3. Download Census Shapefiles

Place Missouri census tract shapefiles in `data/raw/`:

- Download from [Census Bureau TIGER/Line](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
- File: `tl_2020_29_tract.shp` (and associated .dbf, .shx, .prj files)

## Usage

### Run the Pipeline

```bash
# Basic run with base sites
python scripts/run_pipeline.py

# Generate 500 synthetic candidate sites
python scripts/run_pipeline.py --generate-candidates 500

# Use Snowflake for data
python scripts/run_pipeline.py --use-snowflake

# Custom output path
python scripts/run_pipeline.py --output outputs/my_map.html
```

### Upload Data to Snowflake

```bash
python scripts/upload_to_snowflake.py
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
