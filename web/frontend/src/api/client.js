const API_BASE = '/api'

/**
 * Fetch all block groups with their geometries and populations
 */
export async function fetchBlockGroups() {
  const response = await fetch(`${API_BASE}/block-groups`)
  if (!response.ok) {
    throw new Error(`Failed to fetch block groups: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch all candidate sites
 */
export async function fetchCandidates() {
  const response = await fetch(`${API_BASE}/candidates`)
  if (!response.ok) {
    throw new Error(`Failed to fetch candidates: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Run the optimization algorithm
 * @param {Object} params
 * @param {string[]} params.affected_geoids - List of affected block group GEOIDs
 * @param {number} params.radius_miles - Service radius in miles
 * @param {number} params.k - Number of distribution centers to select
 * @param {string[]} params.site_types - Types of sites to consider
 */
export async function runOptimization(params) {
  const response = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    throw new Error(`Optimization failed: ${response.statusText}`)
  }
  return response.json()
}
