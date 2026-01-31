/**
 * Fetch road distance and duration using Google Maps Directions API
 */
export async function getRouteInfo(originLat, originLng, destLat, destLng, directionsService) {
  return new Promise((resolve) => {
    if (!directionsService) {
      resolve(null);
      return;
    }

    directionsService.route(
      {
        origin: { lat: originLat, lng: originLng },
        destination: { lat: destLat, lng: destLng },
        travelMode: window.google.maps.TravelMode.DRIVING,
      },
      (result, status) => {
        if (status === 'OK' && result.routes && result.routes.length > 0) {
          const route = result.routes[0];
          const leg = route.legs[0];
          
          resolve({
            distance: leg.distance.value / 1000, // Convert meters to kilometers
            duration: leg.duration.value / 60, // Convert seconds to minutes
            path: route.overview_path, // Array of LatLng points for drawing polyline
            directions: result, // Full directions result for DirectionsRenderer
          });
        } else {
          console.error('Directions request failed:', status);
          resolve(null);
        }
      }
    );
  });
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

/**
 * Get route info using Distance Matrix API (for bulk distance calculations)
 */
export async function getDistanceMatrix(origin, destinations, distanceMatrixService) {
  return new Promise((resolve) => {
    if (!distanceMatrixService) {
      resolve(null);
      return;
    }

    distanceMatrixService.getDistanceMatrix(
      {
        origins: [origin],
        destinations: destinations,
        travelMode: window.google.maps.TravelMode.DRIVING,
        drivingOptions: {
          departureTime: new Date(), // Required for traffic-aware duration
          trafficModel: 'bestguess', // Options: 'bestguess', 'pessimistic', 'optimistic'
        },
      },
      (response, status) => {
        if (status === 'OK') {
          resolve(response.rows[0].elements);
        } else {
          console.error('Distance Matrix request failed:', status);
          resolve(null);
        }
      }
    );
  });
}
