"""Optimization algorithms for site selection."""
import math
from typing import List, Dict, Any, Set, Tuple


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in miles."""
    R = 3958.7613  # Earth's radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def greedy_max_coverage(
    demand_points: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]],
    radius_miles: float,
    k: int,
) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """
    Greedy algorithm to maximize population coverage.

    Args:
        demand_points: List of block groups with geoid, lat, lon, population
        candidates: List of candidate sites with site_id, name, type, lat, lon
        radius_miles: Maximum service radius
        k: Number of sites to select

    Returns:
        Tuple of (selected_sites, covered_geoids)
    """
    # Build coverage sets: for each candidate, which demand points it covers
    cover_sets: List[List[int]] = []
    demand_indices = list(range(len(demand_points)))

    for cand in candidates:
        covered_indices = []
        cand_lat, cand_lon = cand["lat"], cand["lon"]

        for idx in demand_indices:
            dp = demand_points[idx]
            dist = haversine_miles(cand_lat, cand_lon, dp["lat"], dp["lon"])
            if dist <= radius_miles:
                covered_indices.append(idx)

        cover_sets.append(covered_indices)

    # Greedy selection
    covered: Set[int] = set()
    selected_sites: List[Dict[str, Any]] = []

    for _ in range(k):
        best_gain = 0
        best_site_idx = None

        for site_idx, indices in enumerate(cover_sets):
            # Calculate marginal gain (new population covered)
            gain = sum(
                demand_points[i]["population"]
                for i in indices
                if i not in covered
            )
            if gain > best_gain:
                best_gain = gain
                best_site_idx = site_idx

        if best_site_idx is None or best_gain == 0:
            break

        # Add selected site
        selected_sites.append({
            "site_id": candidates[best_site_idx]["site_id"],
            "name": candidates[best_site_idx]["name"],
            "type": candidates[best_site_idx]["type"],
            "lat": candidates[best_site_idx]["lat"],
            "lon": candidates[best_site_idx]["lon"],
        })

        # Mark points as covered
        for i in cover_sets[best_site_idx]:
            covered.add(i)

        # Clear this site's coverage to prevent reselection
        cover_sets[best_site_idx] = []

    # Get covered GEOIDs
    covered_geoids = {demand_points[i]["geoid"] for i in covered}

    return selected_sites, covered_geoids


def run_optimization(
    block_groups: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]],
    affected_geoids: List[str],
    radius_miles: float,
    k: int,
    site_types: List[str],
) -> Dict[str, Any]:
    """
    Run the full optimization pipeline.

    Args:
        block_groups: All block groups
        candidates: All candidate sites
        affected_geoids: GEOIDs of affected areas
        radius_miles: Service radius
        k: Number of sites to select
        site_types: Types of sites to consider

    Returns:
        Optimization result with metrics and selected sites
    """
    # Filter to affected block groups
    demand_points = [
        bg for bg in block_groups
        if bg["geoid"] in affected_geoids
    ]

    # Filter candidates by type
    filtered_candidates = [
        c for c in candidates
        if c["type"] in site_types
    ]

    if not demand_points:
        return {
            "total_population": 0,
            "covered_population": 0,
            "coverage_percent": 0,
            "selected_sites": [],
        }

    if not filtered_candidates:
        total_pop = sum(dp["population"] for dp in demand_points)
        return {
            "total_population": total_pop,
            "covered_population": 0,
            "coverage_percent": 0,
            "selected_sites": [],
        }

    # Run greedy algorithm
    selected_sites, covered_geoids = greedy_max_coverage(
        demand_points, filtered_candidates, radius_miles, k
    )

    # Calculate metrics
    total_population = sum(dp["population"] for dp in demand_points)
    covered_population = sum(
        dp["population"] for dp in demand_points
        if dp["geoid"] in covered_geoids
    )
    coverage_percent = (
        (covered_population / total_population * 100)
        if total_population > 0
        else 0
    )

    return {
        "total_population": total_population,
        "covered_population": covered_population,
        "coverage_percent": coverage_percent,
        "selected_sites": selected_sites,
    }
