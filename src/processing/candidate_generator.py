"""Generate candidate site locations for optimization."""
import random

import pandas as pd

# Base anchor sites in St. Louis
BASE_SITES = [
    ("church_1", 38.6359, -90.2211),      # Central West End
    ("church_2", 38.6277, -90.1994),      # Downtown
    ("school_1", 38.6460, -90.2547),      # Delmar Loop
    ("school_2", 38.6089, -90.2368),      # Tower Grove
    ("community_1", 38.6701, -90.2846),   # Clayton edge
    ("community_2", 38.5964, -90.2253),   # South City
]

# St. Louis metro bounding box
STL_BBOX = (38.40, 38.90, -90.74, -90.12)  # (min_lat, max_lat, min_lon, max_lon)


def generate_candidates(
    n: int = 500,
    jitter_deg: float = 0.035,
    bbox: tuple | None = None,
    uniform_ratio: float = 0.30,
    include_base: bool = True,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic candidate site locations.

    Creates points either by:
    - Jittering around known base sites (default 70%)
    - Uniform random sampling within bounding box (default 30%)

    Args:
        n: Number of synthetic points to generate
        jitter_deg: Max jitter in degrees (~0.01 deg = ~0.69 miles)
        bbox: (min_lat, max_lat, min_lon, max_lon) for uniform sampling
        uniform_ratio: Fraction of points from uniform sampling
        include_base: Whether to include the original base sites
        seed: Random seed for reproducibility

    Returns:
        DataFrame with site_id, lat, lon columns
    """
    random.seed(seed)
    bbox = bbox or STL_BBOX
    rows = []

    for i in range(n):
        if random.random() < uniform_ratio:
            min_lat, max_lat, min_lon, max_lon = bbox
            lat = random.uniform(min_lat, max_lat)
            lon = random.uniform(min_lon, max_lon)
            tag = "rand"
        else:
            _, b_lat, b_lon = random.choice(BASE_SITES)
            lat = b_lat + random.uniform(-jitter_deg, jitter_deg)
            lon = b_lon + random.uniform(-jitter_deg, jitter_deg)
            tag = "jitter"

        rows.append({
            "site_id": f"site_{tag}_{i+1}",
            "lat": lat,
            "lon": lon,
        })

    if include_base:
        for sid, lat, lon in BASE_SITES:
            rows.append({"site_id": sid, "lat": lat, "lon": lon})

    return pd.DataFrame(rows)


def get_base_sites() -> pd.DataFrame:
    """Return the base anchor sites as a DataFrame."""
    return pd.DataFrame(
        [{"site_id": sid, "lat": lat, "lon": lon} for sid, lat, lon in BASE_SITES]
    )
