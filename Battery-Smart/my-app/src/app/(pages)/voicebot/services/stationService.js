/**
 * Station Service - Handles station data with ETA/traffic calculations
 * 
 * This service:
 * 1. Gets user location
 * 2. Calculates ETA/traffic for all stations using getTrafficAwareRoute
 * 3. Sends data to backend API (single call, cached)
 * 
 * Avoids repetitive Google Maps API calls by calculating once on page load.
 */

import { SWAP_STATIONS } from '../../maps/constants';
import { getTrafficAwareRoute } from '../../maps/utils';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Cache flag to prevent duplicate API calls
let stationDataSent = false;

/**
 * Get user's current location
 * @returns {Promise<{lat: number, lng: number}>}
 */
export async function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
      },
      (error) => {
        console.warn('Location permission denied, using default location');
        // Default: Gurgaon area
        resolve({ lat: 28.4595, lng: 77.0266 });
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  });
}

/**
 * Calculate ETA/traffic for all stations
 * @param {Object} userLocation - {lat, lng}
 * @returns {Promise<Array>} Stations with distance and duration
 */
export async function calculateAllStationRoutes(userLocation) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
  
  if (!apiKey) {
    console.error('Google Maps API key not configured');
    return [];
  }

  console.log('🗺️ Calculating routes for all stations...');
  
  const stationsWithRoutes = await Promise.all(
    SWAP_STATIONS.map(async (station) => {
      try {
        const route = await getTrafficAwareRoute(
          userLocation,
          { lat: station.lat, lng: station.lng },
          apiKey
        );

        if (route) {
          return {
            ...station,
            distance: route.distance, // km
            duration: route.duration, // minutes (traffic-aware ETA)
            isRoadDistance: true
          };
        }
      } catch (error) {
        console.error(`Error fetching route for ${station.name}:`, error);
      }

      // Fallback: straight-line distance calculation
      const distance = calculateStraightLineDistance(
        userLocation.lat,
        userLocation.lng,
        station.lat,
        station.lng
      );
      
      return {
        ...station,
        distance,
        duration: null, // No ETA available
        isRoadDistance: false
      };
    })
  );

  console.log(`✅ Calculated routes for ${stationsWithRoutes.length} stations`);
  return stationsWithRoutes;
}

/**
 * Calculate straight-line distance using Haversine formula
 */
function calculateStraightLineDistance(lat1, lng1, lat2, lng2) {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Send station data to backend API
 * @param {Object} userLocation - {lat, lng}
 * @param {Array} stations - Stations with distance/duration
 * @returns {Promise<Object>} Response from backend
 */
export async function sendStationDataToBackend(userLocation, stations) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/station-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_location: userLocation,
        stations: stations
      })
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const data = await response.json();
    console.log('📍 Station data sent to backend:', data);
    return data;
  } catch (error) {
    console.error('Failed to send station data to backend:', error);
    throw error;
  }
}

/**
 * Initialize station data - call this once on voicebot page load
 * Calculates ETA for all stations and sends to backend (single call)
 * @returns {Promise<{success: boolean, stationCount: number}>}
 */
export async function initializeStationData() {
  // Prevent duplicate calls
  if (stationDataSent) {
    console.log('📍 Station data already sent, skipping...');
    return { success: true, cached: true };
  }

  try {
    console.log('🚀 Initializing station data...');
    
    // Step 1: Get user location
    const userLocation = await getUserLocation();
    console.log(`📍 User location: ${userLocation.lat}, ${userLocation.lng}`);
    
    // Step 2: Calculate ETA for all stations
    const stationsWithRoutes = await calculateAllStationRoutes(userLocation);
    
    // Step 3: Send to backend
    const result = await sendStationDataToBackend(userLocation, stationsWithRoutes);
    
    // Mark as sent
    stationDataSent = true;
    
    console.log('✅ Station data initialization complete');
    return {
      success: true,
      stationCount: stationsWithRoutes.length,
      nearestStation: result.nearest_station,
      bestStation: result.best_station
    };
  } catch (error) {
    console.error('❌ Station data initialization failed:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Reset the cache flag (call when user leaves voicebot page)
 */
export function resetStationDataCache() {
  stationDataSent = false;
}
