/**
 * Traffic-aware routing using Google Routes API
 * Provides per-segment traffic data for colored route visualization
 */

// Traffic speed category to color mapping
export const TRAFFIC_COLORS = {
  NORMAL: '#22c55e',      // Green
  SLOW: '#f59e0b',        // Yellow/Orange
  TRAFFIC_JAM: '#ef4444', // Red
};

/**
 * Decode an encoded polyline string into an array of coordinates
 * @param {string} encoded - The encoded polyline string
 * @returns {Array<{lat: number, lng: number}>} Array of coordinates
 */
export function decodePolyline(encoded) {
  const points = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    let b;
    let shift = 0;
    let result = 0;

    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);

    const dlat = (result & 1) !== 0 ? ~(result >> 1) : result >> 1;
    lat += dlat;

    shift = 0;
    result = 0;

    do {
      b = encoded.charCodeAt(index++) - 63;
      result |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20);

    const dlng = (result & 1) !== 0 ? ~(result >> 1) : result >> 1;
    lng += dlng;

    points.push({
      lat: lat / 1e5,
      lng: lng / 1e5,
    });
  }

  return points;
}

/**
 * Fetch traffic-aware route from Google Routes API
 * @param {Object} origin - {lat, lng} of origin
 * @param {Object} destination - {lat, lng} of destination
 * @param {string} apiKey - Google Maps API key
 * @returns {Promise<Object>} Route data with traffic segments
 */
export async function getTrafficAwareRoute(origin, destination, apiKey) {
  const url = 'https://routes.googleapis.com/directions/v2:computeRoutes';

  const requestBody = {
    origin: {
      location: {
        latLng: {
          latitude: origin.lat,
          longitude: origin.lng,
        },
      },
    },
    destination: {
      location: {
        latLng: {
          latitude: destination.lat,
          longitude: destination.lng,
        },
      },
    },
    travelMode: 'DRIVE',
    routingPreference: 'TRAFFIC_AWARE',
    computeAlternativeRoutes: false,
    extraComputations: ['TRAFFIC_ON_POLYLINE'],
    languageCode: 'en-US',
    units: 'METRIC',
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': apiKey,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline,routes.legs.polyline,routes.travelAdvisory,routes.legs.travelAdvisory',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Routes API error:', response.status, response.statusText);
      console.error('Error details:', JSON.stringify(errorData, null, 2));
      console.error('Make sure Routes API is enabled at: https://console.cloud.google.com/apis/library/routes.googleapis.com');
      return null;
    }

    const data = await response.json();
    
    if (!data.routes || data.routes.length === 0) {
      console.error('No routes found in response:', JSON.stringify(data, null, 2));
      return null;
    }

    const route = data.routes[0];
    const encodedPolyline = route.polyline?.encodedPolyline;
    const speedReadingIntervals = route.travelAdvisory?.speedReadingIntervals || 
                                   route.legs?.[0]?.travelAdvisory?.speedReadingIntervals || [];

    if (!encodedPolyline) {
      console.error('No polyline in response');
      return null;
    }

    // Decode the polyline
    const decodedPath = decodePolyline(encodedPolyline);

    // Build colored segments based on speed reading intervals
    const coloredSegments = buildColoredSegments(decodedPath, speedReadingIntervals);

    return {
      distance: route.distanceMeters / 1000, // km
      duration: parseInt(route.duration?.replace('s', '')) / 60, // minutes
      path: decodedPath,
      coloredSegments,
      speedReadingIntervals,
    };
  } catch (error) {
    console.error('Error fetching traffic-aware route:', error);
    return null;
  }
}

/**
 * Build colored polyline segments from speed reading intervals
 * @param {Array} path - Decoded polyline points
 * @param {Array} intervals - Speed reading intervals from API
 * @returns {Array} Array of {path, color} segments
 */
function buildColoredSegments(path, intervals) {
  if (!intervals || intervals.length === 0) {
    // No traffic data, return single segment in blue
    return [{
      path: path,
      color: '#4285F4', // Google Maps blue
    }];
  }

  const segments = [];

  for (const interval of intervals) {
    const startIndex = interval.startPolylinePointIndex || 0;
    const endIndex = interval.endPolylinePointIndex || path.length - 1;
    const speed = interval.speed || 'NORMAL';

    // Extract path segment
    const segmentPath = path.slice(startIndex, endIndex + 1);
    
    if (segmentPath.length > 0) {
      segments.push({
        path: segmentPath,
        color: TRAFFIC_COLORS[speed] || TRAFFIC_COLORS.NORMAL,
        speed: speed,
      });
    }
  }

  return segments;
}
