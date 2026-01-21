# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

STL Site Optimizer is a Python-based geospatial analysis tool for identifying optimal service locations across St. Louis City and County. It analyzes census block group demographics, vulnerability metrics, and candidate site locations to support data-driven decisions about civic service placement.

The system uses **block group-level granularity** (smaller geographic units than tracts) with comprehensive vulnerability indicators including economic stress, age dependency, housing quality, and infrastructure access.

## Development Environment

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Snowflake (optional, if using Snowflake integration)
cp .env.example .env
# Edit .env with your Snowflake credentials
```

### Required Data

1. **Block Group Shapefiles**: Download from [Census Bureau TIGER/Line](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) and place in `data/raw/`:
   - File: `tl_2020_29_bg.shp` (and associated .dbf, .shx, .prj files)
   - Geographic scope: Missouri (covers St. Louis City FIPS 510 and St. Louis County FIPS 189)

2. **BLOCK_GROUP_DEMOGRAPHICS Data**: Population and vulnerability metrics in Snowflake
   - Source: `data/backup/BLOCK_GROUP_DEMOGRAPHICS.csv` (block group-level demographics)
   - Upload to Snowflake using: `python scripts/upload_pops_data.py`
   - Includes 35+ metrics: population, income, SNAP, age dependency, housing, transportation access, internet access

### Snowflake Setup

```bash
# Upload BLOCK_GROUP_DEMOGRAPHICS data to Snowflake (one-time setup)
python scripts/upload_pops_data.py
```

Requires `.env` with Snowflake credentials (see `cp .env.example .env`)

### Running the Pipeline

```bash
# Basic run with default candidate sites and BLOCK_GROUP_DEMOGRAPHICS data from Snowflake
python scripts/run_pipeline.py

# Generate N synthetic candidate sites
python scripts/run_pipeline.py --generate-candidates 500

# Custom output path
python scripts/run_pipeline.py --output outputs/my_map.html
```

The pipeline automatically loads block group geometries, merges BLOCK_GROUP_DEMOGRAPHICS data from Snowflake, and generates an interactive map. If Snowflake is unavailable, it proceeds with geometry only.

Main entry point: `scripts/run_pipeline.py`

## Architecture

The codebase is organized into three main modules:

### 1. Data Ingestion (`src/data_ingestion/`)

Handles loading and fetching data from multiple sources:

- **shapefile_loader.py**: Loads census block group boundaries from local TIGER/Line shapefiles
  - `load_stl_block_groups()`: Loads block group geometries and filters for St. Louis City (FIPS 510) and County (FIPS 189)
  - `get_default_block_group_shapefile_path()`: Returns path to `tl_2020_29_bg.shp`
  - Returns GeoDataFrame with block group geometries in EPSG:4326
- **census_api.py**: Fetches population data from Census Bureau ACS API (legacy, currently unused)
  - Kept for backward compatibility
  - Retrieves 5-year estimates for demographic analysis
- **snowflake_client.py**: Interface to Snowflake for block group demographics
  - `get_tract_info()`: Fetches BLOCK_GROUP_DEMOGRAPHICS table with 35+ vulnerability metrics
  - Manages connections and queries for candidate sites and BLOCK_GROUP_DEMOGRAPHICS data
  - Reads Snowflake credentials from `.env`
- **__init__.py**: Exports `load_stl_block_groups`, `get_default_block_group_shapefile_path`, and `SnowflakeClient`

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
Block Group Shapefile → load_stl_block_groups() → block group GeoDataFrame
              ↓
          process_tracts() → compute centroids (lat/lon)
              ↓
    Snowflake BLOCK_GROUP_DEMOGRAPHICS table (census_api.get_tract_info()) → 35+ vulnerability metrics
              ↓
          Merge on GEOID → enriched block groups with demographics
              ↓
          get_base_sites() OR generate_candidates() → candidate sites
              ↓
          build_stl_map() → Folium map with popups
              ↓
          save_map() → HTML output (outputs/stl_map.html)
```

## Key Dependencies

- **GeoPandas**: Geospatial data manipulation (extends Pandas for spatial operations)
- **Shapely**: Geometric operations and centroid calculations
- **Folium**: Interactive map visualization
- **Pandas**: Data manipulation and analysis
- **Snowflake Connector**: Database integration for scalable operations
- **Requests**: Census API HTTP requests

## Important Notes for Development

- **GEOID matching**: The project uses GEOID as the primary identifier for block groups. Always cast to string when merging BLOCK_GROUP_DEMOGRAPHICS data with shapefiles to avoid type mismatches.
- **Block group vs. tract**: System uses block groups (smallest census geographic unit) not tracts. This provides finer granularity for service location optimization.
- **BLOCK_GROUP_DEMOGRAPHICS table schema**: 35+ columns including GEOID, Location, POP, and vulnerability metrics. See `data/backup/BLOCK_GROUP_DEMOGRAPHICS_Data_Dictionary.csv` for full documentation.
- **Snowflake integration**: Pipeline gracefully handles Snowflake unavailability—if connection fails, it proceeds with geometry only (no demographic data).
- **Geographic scope**: Fixed to Missouri (FIPS 29), filtered to St. Louis City (510) and County (189).
- **Output format**: All maps saved to `outputs/` directory (created automatically if needed) as interactive HTML files.
- **Python version**: Codebase requires Python 3.10+ for type hints and modern syntax.

## Key Scripts

- `scripts/run_pipeline.py`: Main entry point—loads block groups, fetches BLOCK_GROUP_DEMOGRAPHICS data from Snowflake, generates map
- `scripts/upload_pops_data.py`: One-time utility to load BLOCK_GROUP_DEMOGRAPHICS.csv into Snowflake (run after initial setup)
