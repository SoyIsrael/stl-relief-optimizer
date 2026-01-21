import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'

function Results({ result }) {
  const {
    total_population = 0,
    covered_population = 0,
    coverage_percent = 0,
    selected_sites = [],
  } = result || {}

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        m: 1,
        maxHeight: '250px',
        overflow: 'auto',
      }}
    >
      {/* Metrics */}
      <Box sx={{ display: 'flex', gap: 4, mb: 2 }}>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Affected Population
          </Typography>
          <Typography variant="h6">
            {total_population.toLocaleString()}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Covered Population
          </Typography>
          <Typography variant="h6">
            {covered_population.toLocaleString()}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Coverage
          </Typography>
          <Typography variant="h6" color="primary">
            {coverage_percent.toFixed(1)}%
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">
            Centers Selected
          </Typography>
          <Typography variant="h6">
            {selected_sites.length}
          </Typography>
        </Box>
      </Box>

      {/* Selected Sites Table */}
      {selected_sites.length > 0 && (
        <>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Selected Distribution Centers
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Latitude</TableCell>
                  <TableCell align="right">Longitude</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {selected_sites.map((site, idx) => (
                  <TableRow key={site.site_id || idx}>
                    <TableCell>{site.name}</TableCell>
                    <TableCell>
                      {site.type?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </TableCell>
                    <TableCell align="right">{site.lat?.toFixed(4)}</TableCell>
                    <TableCell align="right">{site.lon?.toFixed(4)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Paper>
  )
}

export default Results
