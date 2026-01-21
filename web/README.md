# STL Disaster Relief Optimizer - Web App

React + FastAPI web application for optimizing disaster relief distribution center placement.

## Project Structure

```
web/
├── frontend/          # React + deck.gl frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map.jsx       # deck.gl map with block groups & sites
│   │   │   ├── Sidebar.jsx   # Controls and filters
│   │   │   └── Results.jsx   # Optimization results display
│   │   ├── api/
│   │   │   └── client.js     # API client for backend
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
└── backend/           # FastAPI backend
    ├── app/
    │   ├── main.py           # FastAPI routes
    │   ├── snowflake_client.py
    │   ├── optimizer.py      # Greedy max coverage algorithm
    │   └── models.py         # Pydantic schemas
    └── requirements.txt
```

## Prerequisites

- Node.js 18+
- Python 3.10+
- Snowflake credentials in `.env` (project root)

## Setup

### Backend

```bash
cd web/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd web/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

## Usage

1. Start the backend (port 8000)
2. Start the frontend (port 3000)
3. Open http://localhost:3000
4. Click on block groups to select affected areas
5. Adjust parameters (radius, number of centers, site types)
6. Click "Run Simulation" to find optimal distribution centers

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/block-groups` | Get all block groups with geometries |
| GET | `/api/candidates` | Get all candidate sites |
| POST | `/api/optimize` | Run optimization algorithm |
| POST | `/api/clear-cache` | Clear data cache |

### Optimization Request Body

```json
{
  "affected_geoids": ["290510001001", "290510001002"],
  "radius_miles": 2.0,
  "k": 5,
  "site_types": ["school", "fire_station", "library"]
}
```

### Optimization Response

```json
{
  "total_population": 15000,
  "covered_population": 12500,
  "coverage_percent": 83.3,
  "selected_sites": [
    {
      "site_id": "site_001",
      "name": "Central High School",
      "type": "school",
      "lat": 38.63,
      "lon": -90.25
    }
  ]
}
```
