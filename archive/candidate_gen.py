import random
import pandas as pd

base = [
    ("church_1", 38.6359, -90.2211),
    ("church_2", 38.6277, -90.1994),
    ("school_1", 38.6460, -90.2547),
    ("school_2", 38.6089, -90.2368),
    ("community_1", 38.6701, -90.2846),
    ("community_2", 38.5964, -90.2253),
]

def make_candidates(n=1000, jitter_deg=0.03, bbox=None, seed=42):
    """
    n: number of generated points
    jitter_deg: ~0.01 deg lat ~ 0.69 miles; 0.03 ~ 2 miles (roughly)
    bbox: (min_lat, max_lat, min_lon, max_lon) optional for uniform sampling
    """
    random.seed(seed)
    rows = []

    for i in range(n):
        # 70%: jitter around a random base site; 30%: uniform in bbox
        if bbox and random.random() < 0.30:
            min_lat, max_lat, min_lon, max_lon = bbox
            lat = random.uniform(min_lat, max_lat)
            lon = random.uniform(min_lon, max_lon)
            tag = "rand"
        else:
            _, b_lat, b_lon = random.choice(base)
            lat = b_lat + random.uniform(-jitter_deg, jitter_deg)
            lon = b_lon + random.uniform(-jitter_deg, jitter_deg)
            tag = "jitter"

        rows.append({
            "site_id": f"site_{tag}_{i+1}",
            "lat": lat,
            "lon": lon
        })

    # include your original sites too
    for sid, lat, lon in base:
        rows.append({"site_id": sid, "lat": lat, "lon": lon})

    return pd.DataFrame(rows)

# STL-ish bbox (adjust if you want tighter/wider)
bbox = (38.40, 38.90, -90.74, -90.12)

df = make_candidates(n=500, jitter_deg=0.035, bbox=bbox, seed=1)
df.to_csv("candidate_sites_big.csv", index=False)
print("Wrote candidate_sites_big.csv with rows:", len(df))
