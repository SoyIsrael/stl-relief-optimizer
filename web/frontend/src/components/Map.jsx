import React, { useMemo } from "react";
import { Map as MapGL } from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { PolygonLayer, ScatterplotLayer } from "@deck.gl/layers";
import { Box, CircularProgress, Typography } from "@mui/material";

// Site type colors (matching your Streamlit app)
const SITE_COLORS = {
  school: [65, 182, 196],
  place_of_worship: [255, 127, 14],
  community_centre: [44, 160, 44],
  fire_station: [214, 39, 40],
  library: [148, 103, 189],
};

// Initial view centered on St. Louis
const INITIAL_VIEW_STATE = {
  longitude: -90.25,
  latitude: 38.63,
  zoom: 10.5,
  pitch: 0,
  bearing: 0,
};

function MapComponent({
  blockGroups,
  candidates,
  selectedGeoids,
  selectedSites,
  onBlockGroupClick,
  loading,
}) {
  // Build polygon data from block groups
  const polygonData = useMemo(() => {
    return blockGroups.map((bg) => ({
      geoid: bg.geoid,
      polygon: bg.polygon,
      population: bg.population,
      isSelected: selectedGeoids.includes(bg.geoid),
    }));
  }, [blockGroups, selectedGeoids]);

  // Selected site IDs for highlighting
  const selectedSiteIds = useMemo(
    () => new Set(selectedSites.map((s) => s.site_id)),
    [selectedSites],
  );

  // Deck.gl layers
  const layers = [
    // Block group polygons (unselected)
    new PolygonLayer({
      id: "block-groups-base",
      data: polygonData.filter((d) => !d.isSelected),
      getPolygon: (d) => d.polygon,
      getFillColor: [200, 200, 200, 40],
      getLineColor: [150, 150, 150],
      getLineWidth: 1,
      lineWidthUnits: "pixels",
      pickable: true,
      autoHighlight: true,
      highlightColor: [100, 150, 250, 100],
      onClick: ({ object }) => object && onBlockGroupClick(object.geoid),
    }),

    // Block group polygons (selected/affected)
    new PolygonLayer({
      id: "block-groups-selected",
      data: polygonData.filter((d) => d.isSelected),
      getPolygon: (d) => d.polygon,
      getFillColor: [255, 140, 0, 100],
      getLineColor: [255, 100, 0],
      getLineWidth: 2,
      lineWidthUnits: "pixels",
      pickable: true,
      onClick: ({ object }) => object && onBlockGroupClick(object.geoid),
    }),

    // Candidate sites (by type)
    new ScatterplotLayer({
      id: "candidates",
      data: candidates.filter((c) => !selectedSiteIds.has(c.site_id)),
      getPosition: (d) => [d.lon, d.lat],
      getRadius: 150,
      getFillColor: (d) => [...(SITE_COLORS[d.type] || [128, 128, 128]), 180],
      pickable: true,
      autoHighlight: true,
    }),

    // Selected distribution centers (green, larger)
    new ScatterplotLayer({
      id: "selected-sites",
      data: selectedSites,
      getPosition: (d) => [d.lon, d.lat],
      getRadius: 300,
      getFillColor: [0, 200, 0, 220],
      pickable: true,
      autoHighlight: true,
    }),
  ];

  // Tooltip content
  const getTooltip = ({ object, layer }) => {
    if (!object) return null;

    if (layer.id.startsWith("block-groups")) {
      return {
        html: `<div>
          <b>Block Group ${object.geoid}</b><br/>
          Population: ${object.population?.toLocaleString() || "N/A"}
        </div>`,
        style: {
          backgroundColor: "white",
          color: "black",
          padding: "8px",
          borderRadius: "4px",
          fontSize: "12px",
        },
      };
    }

    if (layer.id === "candidates" || layer.id === "selected-sites") {
      return {
        html: `<div>
          <b>${object.name}</b><br/>
          ${object.type?.replace("_", " ")}
        </div>`,
        style: {
          backgroundColor: "white",
          color: "black",
          padding: "8px",
          borderRadius: "4px",
          fontSize: "12px",
        },
      };
    }

    return null;
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          flexDirection: "column",
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography>Loading map data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%", height: "100%", overflow: "hidden" }}>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
        getTooltip={getTooltip}
        style={{ width: "100%", height: "100%" }}
      >
        <MapGL
          mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
          attributionControl={false}
        />
      </DeckGL>
    </Box>
  );
}

export default MapComponent;
