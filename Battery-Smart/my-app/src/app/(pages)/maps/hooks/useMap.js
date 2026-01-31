"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { useJsApiLoader } from '@react-google-maps/api';
import { SWAP_STATIONS, DEFAULT_LOCATION, GOOGLE_MAPS_CONFIG } from '../constants';
import { calculateStraightLineDistance, getTrafficAwareRoute } from '../utils';

const libraries = ['places', 'geometry'];

export default function useMap() {
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [nearestStation, setNearestStation] = useState(null);
  const [stationsWithDistance, setStationsWithDistance] = useState([]);
  const [routesLoading, setRoutesLoading] = useState(false);
  const [selectedStation, setSelectedStation] = useState(null);
  const [showTraffic, setShowTraffic] = useState(true);

  const mapRef = useRef(null);
  const polylinesRef = useRef([]); // Store polyline objects for manual management

  // Load Google Maps API
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
    libraries,
  });

  // Get user's current location
  useEffect(() => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser");
      setIsLoading(false);
      setUserLocation(DEFAULT_LOCATION);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lng: longitude });
        setIsLoading(false);
      },
      (error) => {
        console.error("Geolocation error:", error);
        setLocationError("Unable to get your location. Using default location.");
        setUserLocation(DEFAULT_LOCATION);
        setIsLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }, []);

  // Calculate distances using Routes API (traffic-aware)
  useEffect(() => {
    if (!userLocation) return;

    const fetchDistances = async () => {
      setRoutesLoading(true);
      const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

      // Fetch distances for all stations using Routes API
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
                duration: route.duration, // minutes (traffic-aware)
                isRoadDistance: true,
              };
            }
          } catch (error) {
            console.error('Error fetching route for station:', station.name, error);
          }

          // Fallback to straight-line distance
          return {
            ...station,
            distance: calculateStraightLineDistance(
              userLocation.lat, userLocation.lng,
              station.lat, station.lng
            ),
            duration: null,
            isRoadDistance: false,
          };
        })
      );

      const sortedStations = stationsWithRoutes.sort((a, b) => a.distance - b.distance);
      setStationsWithDistance(sortedStations);
      setNearestStation(sortedStations[0]);
      setRoutesLoading(false);
    };

    fetchDistances();
  }, [userLocation]);

  // Helper function to clear all polylines from the map
  const clearPolylines = useCallback(() => {
    polylinesRef.current.forEach(polyline => {
      if (polyline) {
        polyline.setMap(null); // Remove from map
      }
    });
    polylinesRef.current = []; // Clear the array
  }, []);

  // Helper function to draw polylines on the map
  const drawPolylines = useCallback((segments) => {
    if (!mapRef.current || !window.google) return;

    segments.forEach(segment => {
      // Draw border polyline
      const borderPolyline = new window.google.maps.Polyline({
        path: segment.path,
        strokeColor: '#1a365d',
        strokeWeight: 8,
        strokeOpacity: 0.9,
        zIndex: 1,
        map: mapRef.current,
      });
      polylinesRef.current.push(borderPolyline);

      // Draw colored polyline on top
      const coloredPolyline = new window.google.maps.Polyline({
        path: segment.path,
        strokeColor: segment.color,
        strokeWeight: 5,
        strokeOpacity: 0.95,
        zIndex: 2,
        map: mapRef.current,
      });
      polylinesRef.current.push(coloredPolyline);
    });
  }, []);

  // Show route for a specific station
  const showRouteForStation = useCallback(async (station) => {
    if (!userLocation) return;

    // Clear previous polylines first
    clearPolylines();
    setSelectedStation(station);
    
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

    // Get traffic-aware route with colored segments from Routes API
    const trafficRoute = await getTrafficAwareRoute(
      userLocation,
      { lat: station.lat, lng: station.lng },
      apiKey
    );

    if (trafficRoute && trafficRoute.coloredSegments && trafficRoute.coloredSegments.length > 0) {
      drawPolylines(trafficRoute.coloredSegments);
    } else {
      // Fallback: single blue segment for the straight line
      console.warn('Routes API failed for station:', station.name, '- showing straight line');
      drawPolylines([{
        path: [
          { lat: userLocation.lat, lng: userLocation.lng },
          { lat: station.lat, lng: station.lng },
        ],
        color: '#4285F4',
      }]);
    }
  }, [userLocation, clearPolylines, drawPolylines]);

  // Callback when map loads
  const onMapLoad = useCallback((map) => {
    mapRef.current = map;
  }, []);

  // Fit bounds to show user and selected station
  useEffect(() => {
    if (!mapRef.current || !userLocation || !selectedStation) return;

    const bounds = new window.google.maps.LatLngBounds();
    bounds.extend(userLocation);
    bounds.extend({ lat: selectedStation.lat, lng: selectedStation.lng });
    mapRef.current.fitBounds(bounds, { padding: 50 });
  }, [selectedStation, userLocation]);

  // Toggle traffic layer visibility
  const toggleTraffic = useCallback(() => {
    setShowTraffic(prev => !prev);
  }, []);

  return {
    // State
    userLocation,
    locationError,
    isLoading: isLoading || !isLoaded,
    mapReady: isLoaded && !loadError,
    nearestStation,
    stationsWithDistance,
    routesLoading,
    selectedStation,
    loadError,
    showTraffic,
    // Actions
    showRouteForStation,
    onMapLoad,
    toggleTraffic,
    clearPolylines,
  };
}

