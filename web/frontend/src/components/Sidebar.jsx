import React from 'react'
import {
  Box,
  Drawer,
  Typography,
  Slider,
  Button,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Chip,
  IconButton,
  useMediaQuery,
} from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import ClearIcon from '@mui/icons-material/Clear'
import MenuIcon from '@mui/icons-material/Menu'
import CloseIcon from '@mui/icons-material/Close'

const DRAWER_WIDTH = 300

const SITE_TYPE_OPTIONS = [
  { value: 'school', label: 'Schools', color: '#41b6c4' },
  { value: 'place_of_worship', label: 'Places of Worship', color: '#ff7f0e' },
  { value: 'community_centre', label: 'Community Centers', color: '#2ca02c' },
  { value: 'fire_station', label: 'Fire Stations', color: '#d62728' },
  { value: 'library', label: 'Libraries', color: '#9467bd' },
]

function Sidebar({
  siteTypes,
  setSiteTypes,
  radius,
  setRadius,
  numCenters,
  setNumCenters,
  selectedCount,
  onOptimize,
  onClear,
  optimizing,
  loading,
  variant = 'permanent',
  open = true,
  onOpen,
  onClose,
}) {
  const isMobile = useMediaQuery('(max-width: 959px)')
  const handleSiteTypeChange = (value) => {
    setSiteTypes(prev =>
      prev.includes(value)
        ? prev.filter(t => t !== value)
        : [...prev, value]
    )
  }

  const sidebarContent = (
    <>
      {/* Close button for mobile */}
      {isMobile && onClose && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      )}
      {/* Header */}
      <Typography variant="h5" sx={{ mb: 1, fontWeight: 600 }}>
        STL Optimizer
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Disaster Relief Distribution
      </Typography>
    </>
  )

  return (
    <>
      {/* Hamburger menu button for mobile */}
      {isMobile && (
        <Box sx={{ position: 'absolute', top: 16, left: 16, zIndex: 1300 }}>
          <IconButton onClick={onOpen}>
            <MenuIcon />
          </IconButton>
        </Box>
      )}

      {/* Drawer */}
      <Drawer
        variant={variant}
        anchor="left"
        open={variant === 'permanent' || open}
        onClose={onClose}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            p: 2,
          },
        }}
      >
        {sidebarContent}

      <Divider sx={{ mb: 2 }} />

        {/* Simulation Controls */}
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Simulation Controls
        </Typography>

        <Typography variant="body2" sx={{ mt: 2, mb: 1 }}>
          Number of distribution centers: {numCenters}
        </Typography>
        <Slider
          value={numCenters}
          onChange={(_, val) => setNumCenters(val)}
          min={1}
          max={20}
          step={1}
          marks={[
            { value: 1, label: '1' },
            { value: 10, label: '10' },
            { value: 20, label: '20' },
          ]}
          sx={{ mb: 2 }}
        />

        <Typography variant="body2" sx={{ mb: 1 }}>
          Service radius: {radius} miles
        </Typography>
        <Slider
          value={radius}
          onChange={(_, val) => setRadius(val)}
          min={0.25}
          max={10}
          step={0.25}
          marks={[
            { value: 0.25, label: '0.25' },
            { value: 5, label: '5' },
            { value: 10, label: '10' },
          ]}
          sx={{ mb: 2 }}
        />

        <Divider sx={{ my: 2 }} />

        {/* Affected Areas */}
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Affected Areas
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Click on block groups to select/deselect
        </Typography>
        <Chip
          label={`${selectedCount} areas selected`}
          color={selectedCount > 0 ? 'primary' : 'default'}
          size="small"
          sx={{ mb: 2 }}
        />

        <Divider sx={{ my: 2 }} />

        {/* Site Filters */}
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Site Filters
        </Typography>
        <FormGroup>
          {SITE_TYPE_OPTIONS.map(option => (
            <FormControlLabel
              key={option.value}
              control={
                <Checkbox
                  checked={siteTypes.includes(option.value)}
                  onChange={() => handleSiteTypeChange(option.value)}
                  size="small"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: option.color,
                    }}
                  />
                  <Typography variant="body2">{option.label}</Typography>
                </Box>
              }
            />
          ))}
        </FormGroup>

        <Divider sx={{ my: 2 }} />

        {/* Legend */}
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Legend
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: '#00c800',
            }}
          />
          <Typography variant="body2">Selected Sites</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              backgroundColor: '#ff8c00',
            }}
          />
          <Typography variant="body2">Affected Area</Typography>
        </Box>

        {/* Action Buttons */}
        <Box sx={{ mt: 'auto', pt: 2 }}>
          <Button
            variant="contained"
            fullWidth
            startIcon={<PlayArrowIcon />}
            onClick={onOptimize}
            disabled={loading || optimizing || selectedCount === 0}
            sx={{ mb: 1 }}
          >
            {optimizing ? 'Optimizing...' : 'Run Simulation'}
          </Button>
          <Button
            variant="outlined"
            fullWidth
            startIcon={<ClearIcon />}
            onClick={onClear}
            disabled={loading || selectedCount === 0}
          >
            Clear Selection
          </Button>
        </Box>
      </Drawer>
    </>
  )
}

export default Sidebar
