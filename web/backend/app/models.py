from pydantic import BaseModel
from typing import List, Optional


class BlockGroup(BaseModel):
    geoid: str
    lat: float
    lon: float
    population: float
    polygon: List  # GeoJSON coordinates


class CandidateSite(BaseModel):
    site_id: str
    name: str
    type: str
    lat: float
    lon: float


class OptimizationRequest(BaseModel):
    affected_geoids: List[str]
    radius_miles: float = 2.0
    k: int = 5
    site_types: List[str] = ["school", "place_of_worship", "community_centre", "fire_station", "library"]


class SelectedSite(BaseModel):
    site_id: str
    name: str
    type: str
    lat: float
    lon: float


class OptimizationResult(BaseModel):
    total_population: float
    covered_population: float
    coverage_percent: float
    selected_sites: List[SelectedSite]
