# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

STL Site Optimizer is a Python-based geospatial analysis tool for identifying optimal service locations across St. Louis City and County. It analyzes census block group demographics, vulnerability metrics, and candidate site locations to support data-driven decisions about civic service placement.

**Key Features:**
- Block group-level granularity (1062 geographic units vs. ~300 tracts) for precise optimization
- Comprehensive vulnerability metrics: economic stress, age dependency, housing quality, infrastructure access
- Centralized Snowflake data warehouse for scalable operations
- Interactive map visualization with demographic popups

## Applications

### Main App: React Web Application (`web/`)

**Primary entry point for users.** Interactive web app with deck.gl map visualization, real-time controls, and responsive mobile design.

- **Frontend**: React + Vite + Material UI + deck.gl
- **Backend**: FastAPI + Snowflake connector
- **Features**: Click-to-select block groups, greedy optimization algorithm, live results display
- **Setup**: See `web/README.md`

### Legacy: Python Streamlit App (`archive/streamlit.py`)

Historical reference implementation. Fully functional but deprecated in favor of the React web app. Uses PyDeck for map visualization.

---

## Development Environment

### Backend Setup (Python)

```bash
# For web app backend
cd web/backend
python -m venv venv
venv\Scripts\activate  # Windows or source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Configure Snowflake credentials
cp .env.example .env
# Edit .env with your Snowflake credentials
```

### Frontend Setup (React)

```bash
# For web app frontend
cd web/frontend
npm install
npm run dev  # Starts dev server on http://localhost:3000
```

### Required Data in Snowflake

All geospatial and demographic data is stored in Snowflake for centralized, scalable access:

1. **BLOCK_GROUP_BOUNDARIES** (1062 rows)
   - Source: `tl_2020_29_bg.shp` shapefile
   - Columns: GEOID, STATEFP, COUNTYFP, TRACTCE, BLKGRPCE, lat, lon, geom_geojson
   - Contains block group geometries as GeoJSON

2. **BLOCK_GROUP_DEMOGRAPHICS** (1062 rows)
   - Source: `data/backup/POPS.csv` (created by Mahfud)
   - Includes: 35+ vulnerability metrics (population, income, SNAP, age dependency, housing, transportation, internet)
   - Joined with boundaries on GEOID

3. **CANDIDATE_SITES** (1000 rows)
   - Predefined service location candidates

### Snowflake Initial Setup

```bash
# One-time setup (after configuring .env with credentials)
python scripts/upload_boundaries.py      # Upload block group geometries from shapefile
python scripts/upload_pops_data.py       # Upload demographics and vulnerability metrics
```

Configure `.env` with Snowflake credentials: `cp .env.example .env`

### Running the Pipeline

```bash
# Basic run (loads block groups and demographics from Snowflake)
python scripts/run_pipeline.py

# Generate N synthetic candidate sites
python scripts/run_pipeline.py --generate-candidates 500

# Use local shapefile instead of Snowflake (fallback)
python scripts/run_pipeline.py --use-local-shapefile

# Custom output path
python scripts/run_pipeline.py --output outputs/my_map.html
```

**Pipeline flow:**
1. Loads block group geometries from **Snowflake** (BLOCK_GROUP_BOUNDARIES) by default
2. Merges demographics from **Snowflake** (BLOCK_GROUP_DEMOGRAPHICS)
3. Falls back to local shapefile if Snowflake unavailable
4. Generates interactive HTML map with demographic popups

Main entry point: `scripts/run_pipeline.py`

## Architecture

The codebase is organized into three main modules:

### 1. Data Ingestion (`src/data_ingestion/`)

Handles loading and fetching data from Snowflake (primary) or local shapefiles (fallback):

- **shapefile_loader.py**: Loads census block group boundaries from multiple sources
  - `load_stl_block_groups()`: Loads from local `tl_2020_29_bg.shp` shapefile (fallback)
  - `load_stl_block_groups_from_snowflake()`: **Primary method** - loads geometries from BLOCK_GROUP_BOUNDARIES table, reconstructs GeoJSON
  - `get_default_block_group_shapefile_path()`: Returns path to `tl_2020_29_bg.shp`
  - Returns GeoDataFrame with block group geometries in EPSG:4326
- **snowflake_client.py**: Central interface to Snowflake data warehouse
  - `get_boundaries()`: Fetches BLOCK_GROUP_BOUNDARIES (geometries as GeoJSON)
  - `get_tract_info()`: Fetches BLOCK_GROUP_DEMOGRAPHICS (35+ vulnerability metrics)
  - `get_candidate_sites()`: Fetches CANDIDATE_SITES
  - Manages connections and queries; reads credentials from `.env`
- **census_api.py**: Fetches population data from Census Bureau ACS API (legacy, unused)
  - Kept for backward compatibility
- **__init__.py**: Exports all loading functions and SnowflakeClient

### 2. Processing (`src/processing/`)

Transforms and generates data:

- **tract_processor.py**: Processes block group data
  - `process_tracts()`: Computes block group centroids and adds lat/lon columns for visualization
  - `compute_centroids()`: Calculates centroid coordinates for each block group geometry
- **candidate_generator.py**: Generates or loads candidate service locations
  - `generate_candidates(n)`: Creates N synthetic candidate sites with random coordinates within St. Louis
  - `get_base_sites()`: Returns predefined candidate sites (real distribution centers, etc.)
- **__init__.py**: Exports processing functions

### 3. Visualization (`src/visualization/`)

Generates interactive maps:

- **map_builder.py**: Creates Folium-based interactive maps
  - `build_stl_map(block_groups, candidates)`: Builds map with block group boundaries and candidate sites
  - Renders block group demographics in HTML popups including population, income, vulnerability metrics
  - `_build_popup_text(row)`: Helper that formats demographic data for display (income, poverty rates, dependency rates, housing metrics, internet access)
  - Marks candidate sites with blue markers
  - `save_map(m, path)`: Saves Folium map to HTML file
- **__init__.py**: Exports map building functions

### Data Flow

```
PRIMARY (Snowflake):
  BLOCK_GROUP_BOUNDARIES → load_stl_block_groups_from_snowflake()
              ↓
          Reconstruct geometries from GeoJSON → block group GeoDataFrame
              ↓
          process_tracts() → use/compute centroids
              ↓
  BLOCK_GROUP_DEMOGRAPHICS → get_tract_info() → 35+ vulnerability metrics
              ↓
          Merge on GEOID → enriched block groups
              ↓
          get_base_sites() OR generate_candidates() → candidate sites
              ↓
          build_stl_map() → Folium map with popups
              ↓
          save_map() → HTML output (outputs/stl_map.html)

FALLBACK (Local):
  [if Snowflake unavailable] Local tl_2020_29_bg.shp → load_stl_block_groups()
```

## Key Dependencies

- **GeoPandas**: Geospatial data manipulation (extends Pandas for spatial operations)
- **Shapely**: Geometric operations and centroid calculations
- **Folium**: Interactive map visualization
- **Pandas**: Data manipulation and analysis
- **Snowflake Connector**: Database integration for scalable operations
- **Requests**: Census API HTTP requests

## Important Notes for Development

- **Snowflake-first architecture**: Block group boundaries and demographics are stored in Snowflake (BLOCK_GROUP_BOUNDARIES, BLOCK_GROUP_DEMOGRAPHICS) as the primary data source for team collaboration and version control.
- **Geometry storage**: Geometries stored as GeoJSON in BLOCK_GROUP_BOUNDARIES.geom_geojson column; automatically reconstructed into Shapely geometries by `load_stl_block_groups_from_snowflake()`.
- **GEOID matching**: All tables joined on GEOID (12-digit string: state + county + tract + block group). Always cast to string to avoid type mismatches.
- **Centroids pre-computed**: BLOCK_GROUP_BOUNDARIES includes lat/lon columns from shapefile centroid calculation; `process_tracts()` recomputes if needed.
- **Block group vs. tract**: System uses block groups (1062 units) not tracts (~300 units). Provides finer granularity for service optimization.
- **Schema documentation**: See `data/backup/POPS_Data_Dictionary.csv` for BLOCK_GROUP_DEMOGRAPHICS column descriptions (35+ metrics).
- **Fallback handling**: If Snowflake unavailable, pipeline falls back to local shapefile (`tl_2020_29_bg.shp`). Still requires demographics for full functionality.
- **Geographic scope**: Fixed to Missouri (FIPS 29), filtered to St. Louis City (510) and County (189).
- **Output format**: All maps saved to `outputs/` directory (auto-created) as interactive HTML files.
- **Python version**: Requires Python 3.10+ for type hints and modern syntax.

## Key Scripts

- `scripts/run_pipeline.py`: Main entry point—loads block groups from Snowflake, merges demographics, generates map. Falls back to local shapefile if Snowflake unavailable.
- `scripts/upload_boundaries.py`: One-time utility to load block group geometries from `tl_2020_29_bg.shp` into BLOCK_GROUP_BOUNDARIES table
- `scripts/upload_pops_data.py`: One-time utility to load `POPS.csv` into BLOCK_GROUP_DEMOGRAPHICS table
- `scripts/cleanup_snowflake.py`: Cleanup utility to remove legacy/duplicate tables
