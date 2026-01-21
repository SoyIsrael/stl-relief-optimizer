import React, { useState, useEffect } from 'react'
import { Box, Alert, useMediaQuery } from '@mui/material'
import Map from './components/Map'
import Sidebar from './components/Sidebar'
import Results from './components/Results'
import { fetchBlockGroups, fetchCandidates, runOptimization } from './api/client'

function App() {
  // Responsive
  const isDesktop = useMediaQuery('(min-width: 960px)')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Data state
  const [blockGroups, setBlockGroups] = useState([])
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Selection state
  const [selectedGeoids, setSelectedGeoids] = useState([])
  const [siteTypes, setSiteTypes] = useState([
    'school', 'place_of_worship', 'community_centre', 'fire_station', 'library'
  ])

  // Optimization parameters
  const [radius, setRadius] = useState(2.0)
  const [numCenters, setNumCenters] = useState(5)

  // Results state
  const [optimizationResult, setOptimizationResult] = useState(null)
  const [optimizing, setOptimizing] = useState(false)

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const [bgData, candData] = await Promise.all([
          fetchBlockGroups(),
          fetchCandidates()
        ])
        setBlockGroups(bgData)
        setCandidates(candData)
        setError(null)
      } catch (err) {
        setError('Failed to load data. Make sure the backend is running.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  // Run optimization
  const handleOptimize = async () => {
    if (selectedGeoids.length === 0) {
      setError('Please select at least one affected area')
      return
    }

    try {
      setOptimizing(true)
      setError(null)
      const result = await runOptimization({
        affected_geoids: selectedGeoids,
        radius_miles: radius,
        k: numCenters,
        site_types: siteTypes
      })
      setOptimizationResult(result)
    } catch (err) {
      setError('Optimization failed. Check console for details.')
      console.error(err)
    } finally {
      setOptimizing(false)
    }
  }

  // Toggle block group selection
  const handleBlockGroupClick = (geoid) => {
    setSelectedGeoids(prev =>
      prev.includes(geoid)
        ? prev.filter(g => g !== geoid)
        : [...prev, geoid]
    )
  }

  // Clear selection
  const handleClearSelection = () => {
    setSelectedGeoids([])
    setOptimizationResult(null)
  }

  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100%', overflow: 'hidden' }}>
      {/* Sidebar */}
      {isDesktop && (
        <Sidebar
          siteTypes={siteTypes}
          setSiteTypes={setSiteTypes}
          radius={radius}
          setRadius={setRadius}
          numCenters={numCenters}
          setNumCenters={setNumCenters}
          selectedCount={selectedGeoids.length}
          onOptimize={handleOptimize}
          onClear={handleClearSelection}
          optimizing={optimizing}
          loading={loading}
          variant="permanent"
        />
      )}
      {!isDesktop && (
        <Sidebar
          siteTypes={siteTypes}
          setSiteTypes={setSiteTypes}
          radius={radius}
          setRadius={setRadius}
          numCenters={numCenters}
          setNumCenters={setNumCenters}
          selectedCount={selectedGeoids.length}
          onOptimize={handleOptimize}
          onClear={handleClearSelection}
          optimizing={optimizing}
          loading={loading}
          variant="temporary"
          open={sidebarOpen}
          onOpen={() => setSidebarOpen(true)}
          onClose={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Error alert */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ m: 1 }}>
            {error}
          </Alert>
        )}

        {/* Map */}
        <Box sx={{ flex: 1, position: 'relative' }}>
          <Map
            blockGroups={blockGroups}
            candidates={candidates.filter(c => siteTypes.includes(c.type))}
            selectedGeoids={selectedGeoids}
            selectedSites={optimizationResult?.selected_sites || []}
            onBlockGroupClick={handleBlockGroupClick}
            loading={loading}
          />
        </Box>

        {/* Results panel */}
        {optimizationResult && (
          <Results result={optimizationResult} />
        )}
      </Box>
    </Box>
  )
}

export default App
