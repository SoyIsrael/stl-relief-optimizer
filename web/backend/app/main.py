"""FastAPI backend for STL Disaster Relief Optimizer."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import (
    BlockGroup,
    CandidateSite,
    OptimizationRequest,
    OptimizationResult,
)
from .snowflake_client import get_client
from .optimizer import run_optimization

app = FastAPI(
    title="STL Disaster Relief Optimizer API",
    description="API for optimizing disaster relief distribution center placement",
    version="0.1.0",
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for data (simple in-memory cache)
_block_groups_cache = None
_candidates_cache = None


def get_block_groups_cached():
    """Get block groups with caching."""
    global _block_groups_cache
    if _block_groups_cache is None:
        client = get_client()
        _block_groups_cache = client.get_block_groups()
    return _block_groups_cache


def get_candidates_cached():
    """Get candidates with caching."""
    global _candidates_cache
    if _candidates_cache is None:
        client = get_client()
        _candidates_cache = client.get_candidates()
    return _candidates_cache


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "STL Optimizer API"}


@app.get("/api/block-groups", response_model=List[BlockGroup])
async def get_block_groups():
    """
    Get all block groups with their geometries and populations.
    Used by the frontend to render the map.
    """
    try:
        data = get_block_groups_cached()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/candidates", response_model=List[CandidateSite])
async def get_candidates():
    """
    Get all candidate distribution sites.
    """
    try:
        data = get_candidates_cached()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize", response_model=OptimizationResult)
async def optimize(request: OptimizationRequest):
    """
    Run the optimization algorithm to select distribution centers.

    The algorithm uses a greedy max-coverage approach to maximize
    the population served within the given radius.
    """
    try:
        block_groups = get_block_groups_cached()
        candidates = get_candidates_cached()

        result = run_optimization(
            block_groups=block_groups,
            candidates=candidates,
            affected_geoids=request.affected_geoids,
            radius_miles=request.radius_miles,
            k=request.k,
            site_types=request.site_types,
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-cache")
async def clear_cache():
    """Clear the data cache (useful during development)."""
    global _block_groups_cache, _candidates_cache
    _block_groups_cache = None
    _candidates_cache = None
    return {"status": "ok", "message": "Cache cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
