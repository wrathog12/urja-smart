import { OSRM_CONFIG } from '../constants';

/**
 * Fetch road distance and duration using OSRM (Open Source Routing Machine) API
 */
export async function getRouteInfo(originLat, originLng, destLat, destLng) {
  try {
    // OSRM expects coordinates in lng,lat format
    const url = `${OSRM_CONFIG.baseUrl}/${originLng},${originLat};${destLng},${destLat}?overview=full&geometries=geojson`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
      const route = data.routes[0];
      return {
        distance: route.distance / 1000, // Convert meters to kilometers
        duration: route.duration / 60, // Convert seconds to minutes
        geometry: route.geometry, // Route geometry for drawing on map
      };
    }
    return null;
  } catch (error) {
    console.error('Error fetching route:', error);
    return null;
  }
}

/**
 * Fallback: Haversine formula for straight-line distance (used if API fails)
 */
export function calculateStraightLineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c; // Distance in kilometers
}
