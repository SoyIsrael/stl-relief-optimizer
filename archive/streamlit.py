import math
import json
import pandas as pd
import pydeck as pdk
import streamlit as st
from snowflake.snowpark.context import get_active_session

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(layout="wide")
st.title("Disaster Relief Distribution Optimizer")

session = get_active_session()

# -----------------------------
# Table names (EDIT IF NEEDED)
# Updated for block group architecture (2025)
# -----------------------------
BOUNDARIES_TABLE = "BLOCK_GROUP_BOUNDARIES"
POPS_TABLE = "BLOCK_GROUP_DEMOGRAPHICS"
CANDIDATES_TABLE = "CANDIDATE_SITES"

# -----------------------------
# Site type colors
# -----------------------------
SITE_COLORS = {
    "school": [65, 182, 196],           # Teal
    "place_of_worship": [255, 127, 14], # Orange
    "community_centre": [44, 160, 44],  # Green
    "fire_station": [214, 39, 40],      # Red
    "library": [148, 103, 189],         # Purple
}

# -----------------------------
# Helpers
# -----------------------------
def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.7613
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def greedy_max_coverage(demand, candidates, radius_miles, k):
    cover_sets = []
    demand_idx = list(demand.index)

    for _, s in candidates.iterrows():
        idxs = []
        s_lat, s_lon = float(s["LAT"]), float(s["LON"])
        for i in demand_idx:
            d_lat, d_lon = float(demand.loc[i, "LAT"]), float(demand.loc[i, "LON"])
            if haversine_miles(s_lat, s_lon, d_lat, d_lon) <= radius_miles:
                idxs.append(i)
        cover_sets.append(idxs)

    covered = set()
    selected_rows = []

    for _ in range(int(k)):
        best_gain, best_site = 0, None

        for j, idxs in enumerate(cover_sets):
            gain = sum(float(demand.loc[i, "POP"]) for i in idxs if i not in covered)
            if gain > best_gain:
                best_gain, best_site = gain, j

        if best_site is None or best_gain == 0:
            break

        selected_rows.append({
            "SITE_ID": candidates.iloc[best_site]["SITE_ID"],
            "NAME": candidates.iloc[best_site]["NAME"],
            "TYPE": candidates.iloc[best_site]["TYPE"],
            "LAT": float(candidates.iloc[best_site]["LAT"]),
            "LON": float(candidates.iloc[best_site]["LON"]),
        })

        for i in cover_sets[best_site]:
            covered.add(i)

        cover_sets[best_site] = []

    selected_sites_df = pd.DataFrame(selected_rows)
    covered_mask = demand.index.isin(list(covered))
    return selected_sites_df, covered_mask

def build_polygons(boundaries):
    rows = []
    for _, r in boundaries.iterrows():
        if not r.GEOM_GEOJSON:
            continue
        try:
            geom = json.loads(r.GEOM_GEOJSON)
            if geom["type"] == "Polygon":
                rows.append({
                    "geoid": r.GEOID,
                    "pop": r.POP,
                    "polygon": geom["coordinates"][0]
                })
            elif geom["type"] == "MultiPolygon":
                for p in geom["coordinates"]:
                    rows.append({
                        "geoid": r.GEOID,
                        "pop": r.POP,
                        "polygon": p[0]
                    })
        except Exception:
            pass
    return pd.DataFrame(rows)

# -----------------------------
# Load data from Snowflake
# -----------------------------
boundaries = session.sql(f"""
    SELECT
        TO_VARCHAR(b.GEOID) AS GEOID,
        b.GEOM_GEOJSON,
        b.LAT::FLOAT AS LAT,
        b.LON::FLOAT AS LON,
        COALESCE(p.POP::FLOAT, 0) AS POP
    FROM {BOUNDARIES_TABLE} b
    LEFT JOIN {POPS_TABLE} p
      ON TO_VARCHAR(b.GEOID) = TO_VARCHAR(p.GEOID)
""").to_pandas()

candidates = session.sql(f"""
    SELECT
        "site_id" AS SITE_ID,
        "name" AS NAME,
        "type" AS TYPE,
        "lat"::FLOAT AS LAT,
        "lon"::FLOAT AS LON
    FROM {CANDIDATES_TABLE}
""").to_pandas()

# Clean up type names for display
candidates["TYPE_DISPLAY"] = candidates["TYPE"].str.replace("_", " ").str.title()

# -----------------------------
# Sidebar GUI
# -----------------------------
with st.sidebar:
    st.header("Simulation Controls")

    k = st.number_input(
        "Number of distribution centers",
        min_value=1,
        max_value=50,
        value=5,
        step=1
    )

    radius = st.slider(
        "Service radius (miles)",
        min_value=0.25,
        max_value=10.0,
        value=2.0,
        step=0.25
    )

    st.divider()
    st.header("Affected Areas")

    affected_geoids = st.multiselect(
        "Select affected GEOIDs",
        options=sorted(boundaries.GEOID.unique().tolist())
    )

    st.divider()
    st.header("Site Filters")

    site_type_options = ["school", "place_of_worship", "community_centre", "fire_station", "library"]
    site_types = st.multiselect(
        "Show site types",
        options=site_type_options,
        default=site_type_options,
        format_func=lambda x: x.replace("_", " ").title()
    )

    marker_opacity = st.slider(
        "Site marker opacity",
        min_value=0.1,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    st.divider()
    st.header("Legend")
    st.markdown("""
    <div style="line-height: 2.0; font-size: 14px;">
        <span style="color: #41b6c4; font-size: 18px;">●</span> Schools<br/>
        <span style="color: #ff7f0e; font-size: 18px;">●</span> Places of Worship<br/>
        <span style="color: #2ca02c; font-size: 18px;">●</span> Community Centers<br/>
        <span style="color: #d62728; font-size: 18px;">●</span> Fire Stations<br/>
        <span style="color: #9467bd; font-size: 18px;">●</span> Libraries<br/>
        <span style="color: #00c800; font-size: 18px;">●</span> <b>Selected Sites</b><br/>
        <span style="color: #ff8c00; font-size: 18px;">■</span> Affected Area
    </div>
    """, unsafe_allow_html=True)

    run = st.button("Run Simulation", type="primary")

# -----------------------------
# Filter candidates by type
# -----------------------------
candidates_filtered = candidates[candidates.TYPE.isin(site_types)].copy()

# -----------------------------
# Demand selection
# -----------------------------
demand = boundaries[boundaries.GEOID.isin(affected_geoids)].copy()

# -----------------------------
# Run simulation
# -----------------------------
selected_sites = pd.DataFrame(columns=["SITE_ID", "NAME", "TYPE", "LAT", "LON"])
covered_mask = pd.Series(dtype=bool)

if run and len(demand) > 0:
    selected_sites, covered_mask = greedy_max_coverage(
        demand, candidates_filtered, radius, k
    )

# -----------------------------
# Metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

total_pop = demand.POP.sum()
covered_pop = demand.loc[covered_mask, "POP"].sum() if run else 0
coverage_pct = (covered_pop / total_pop * 100) if total_pop > 0 else 0

col1.metric("Affected Population", f"{total_pop:,.0f}")
col2.metric("Covered Population", f"{covered_pop:,.0f}")
col3.metric("Coverage", f"{coverage_pct:.1f}%")
col4.metric("Centers Selected", len(selected_sites))

# -----------------------------
# Build map layers
# -----------------------------
layers = []

polys = build_polygons(boundaries)
polys["selected"] = polys.geoid.isin(affected_geoids)
polys["NAME"] = "Tract " + polys["geoid"].astype(str)
polys["TYPE_DISPLAY"] = "Census Tract (Pop: " + polys["pop"].astype(int).astype(str) + ")"

# Base polygons (unselected) - low opacity to show base map
layers.append(
    pdk.Layer(
        "PolygonLayer",
        polys[~polys.selected],
        get_polygon="polygon",
        filled=True,
        stroked=True,
        get_fill_color=[200, 200, 200, 40],
        get_line_color=[150, 150, 150],
        get_line_width=20,
        pickable=True,
        auto_highlight=True,
    )
)

# Selected polygons (affected areas)
layers.append(
    pdk.Layer(
        "PolygonLayer",
        polys[polys.selected],
        get_polygon="polygon",
        filled=True,
        stroked=True,
        get_fill_color=[255, 140, 0, 80],
        get_line_color=[255, 100, 0],
        get_line_width=40,
        pickable=True,
    )
)

# Demand centroids
if len(demand) > 0:
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            demand,
            get_position="[LON, LAT]",
            get_radius=100,
            get_fill_color=[200, 0, 0, 180],
            pickable=False,
        )
    )

# Candidate sites (separate layer per type for reliable colors)
for site_type, color in SITE_COLORS.items():
    type_data = candidates_filtered[candidates_filtered.TYPE == site_type]
    if len(type_data) > 0:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                type_data,
                get_position="[LON, LAT]",
                get_radius=150,
                get_fill_color=color + [int(255 * marker_opacity)],
                pickable=True,
                auto_highlight=True,
            )
        )

# Selected sites (green, larger)
if run and len(selected_sites) > 0:
    selected_sites["TYPE_DISPLAY"] = selected_sites["TYPE"].str.replace("_", " ").str.title()
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            selected_sites,
            get_position="[LON, LAT]",
            get_radius=300,
            get_fill_color=[0, 200, 0, 220],
            pickable=True,
            auto_highlight=True,
        )
    )

# -----------------------------
# Render map
# -----------------------------
view_state = pdk.ViewState(
    latitude=boundaries.LAT.mean(),
    longitude=boundaries.LON.mean(),
    zoom=10.7
)

tooltip = {
    "html": """
        <div style="font-family: sans-serif; padding: 4px;">
            <b>{NAME}</b><br/>
            <span style="color: #666;">{TYPE_DISPLAY}</span>
        </div>
    """,
    "style": {"backgroundColor": "white", "color": "black", "border": "1px solid #ccc"}
}

deck = pdk.Deck(
    map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
    initial_view_state=view_state,
    layers=layers,
    tooltip=tooltip,
)

st.pydeck_chart(deck, use_container_width=True)

# -----------------------------
# Results table
# -----------------------------
if run and len(selected_sites) > 0:
    st.subheader("Selected Distribution Centers")
    display_df = selected_sites[["NAME", "TYPE", "LAT", "LON"]].copy()
    display_df.columns = ["Name", "Type", "Latitude", "Longitude"]
    display_df["Type"] = display_df["Type"].str.replace("_", " ").str.title()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
