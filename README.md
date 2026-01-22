# STL Disaster Relief Distribution Optimizer

Geospatial optimization tool for identifying optimal disaster relief distribution center locations across St. Louis City and County.

## Quick Start

### Web Application (Main)

The primary interface is a React web app with an interactive deck.gl map for selecting affected areas and optimizing center placement.

```bash
# Terminal 1 - Backend API
cd web/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd web/frontend
npm install
npm run dev
```

Open http://localhost:3000 to access the app.

**Features:**
- Click block groups on the map to select affected areas
- Adjust service radius and number of distribution centers
- Filter by site type (schools, fire stations, libraries, etc.)
- Responsive design (desktop/mobile)
- Real-time optimization results with population coverage metrics

## Architecture

### Data
- **Block Groups**: 1,062 census units (St. Louis City + County)
- **Demographics**: Population, vulnerability metrics (income, age, housing, internet access)
- **Candidate Sites**: ~1,000 predefined location options
- **Storage**: Snowflake data warehouse

### Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + Material UI + deck.gl |
| Backend | FastAPI + Python |
| Database | Snowflake |
| Algorithm | Greedy max-coverage optimization |

### File Structure
```
.
├── web/                          # Main React + FastAPI web app
│   ├── frontend/                 # React app (npm)
│   │   └── src/components/       # Map, Sidebar, Results
│   └── backend/                  # FastAPI server
│       └── app/                  # Routes, optimization, data client
│
├── src/                          # Python data pipeline (legacy)
│   ├── data_ingestion/           # Snowflake client
│   ├── processing/               # Centroid & candidate generation
│   └── visualization/            # Folium map builder
│
├── scripts/                      # Utility scripts
│   ├── run_pipeline.py          # Generate static maps
│   ├── upload_boundaries.py     # Load boundaries to Snowflake
│   └── upload_pops_data.py      # Load demographics to Snowflake
│
└── archive/                      # Historical reference
    └── streamlit.py              # Legacy Streamlit app
```

## Data Setup

**Required Snowflake tables:**
1. **BLOCK_GROUP_BOUNDARIES** - Geometries (GeoJSON) + lat/lon
2. **BLOCK_GROUP_DEMOGRAPHICS** - Population + 35+ vulnerability metrics
3. **BLOCK_GROUP_DEMOGRAPHICS_COUNTY** - County-specific demographics
4. **CANDIDATE_SITES** - Service location candidates

**To load initial data:**
```bash
python scripts/upload_boundaries.py
python scripts/upload_pops_data.py
```

Configure `.env` with Snowflake credentials first:
```bash
cp .env.example .env
# Edit with your Snowflake account details
```

## Development

### Key Files
- `web/README.md` - Web app setup and API reference
- `.env.example` - Snowflake configuration template

## Algorithm

Greedy max-coverage optimization:
1. Filter demand (affected block groups) and candidate sites
2. For each candidate, calculate which block groups it can serve (within radius)
3. Iteratively select the candidate covering the most uncovered population
4. Continue until K sites selected or all population covered

Result: Population coverage % and list of selected distribution centers.

## Project Status

✅ Full data coverage: 314 City + 748 County = 1,062 block groups
✅ Complete API endpoints
✅ Interactive React web app with mobile support
✅ Responsive sidebar with mobile drawer
✅ Real-time optimization

## License

Internal project - St. Louis disaster relief optimization.
