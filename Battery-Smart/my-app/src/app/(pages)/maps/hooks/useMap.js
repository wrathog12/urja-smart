"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { SWAP_STATIONS, DEFAULT_LOCATION, MAP_CONFIG, LEAFLET_CDN, ROUTE_STYLES } from '../constants';
import { getRouteInfo, calculateStraightLineDistance } from '../utils';

export default function useMap() {
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [nearestStation, setNearestStation] = useState(null);
  const [stationsWithDistance, setStationsWithDistance] = useState([]);
  const [routesLoading, setRoutesLoading] = useState(false);
  const [selectedStation, setSelectedStation] = useState(null);
  
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const routeLayersRef = useRef([]);
  const leafletRef = useRef(null);

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

  // Calculate road distances using OSRM API
  useEffect(() => {
    if (!userLocation) return;

    const fetchRouteDistances = async () => {
      setRoutesLoading(true);
      
      const stationsWithRoutes = await Promise.all(
        SWAP_STATIONS.map(async (station) => {
          const routeInfo = await getRouteInfo(
            userLocation.lat, userLocation.lng,
            station.lat, station.lng
          );
          
          if (routeInfo) {
            return {
              ...station,
              distance: routeInfo.distance,
              duration: routeInfo.duration,
              geometry: routeInfo.geometry,
              isRoadDistance: true,
            };
          } else {
            return {
              ...station,
              distance: calculateStraightLineDistance(
                userLocation.lat, userLocation.lng,
                station.lat, station.lng
              ),
              duration: null,
              geometry: null,
              isRoadDistance: false,
            };
          }
        })
      );

      const sortedStations = stationsWithRoutes.sort((a, b) => a.distance - b.distance);
      
      setStationsWithDistance(sortedStations);
      setNearestStation(sortedStations[0]);
      setRoutesLoading(false);
    };

    fetchRouteDistances();
  }, [userLocation]);

  // Function to show route for a specific station
  const showRouteForStation = useCallback((station) => {
    if (!mapInstanceRef.current || !leafletRef.current || !userLocation) return;
    
    const L = leafletRef.current;
    
    // Clear existing routes
    routeLayersRef.current.forEach(layer => {
      mapInstanceRef.current.removeLayer(layer);
    });
    routeLayersRef.current = [];
    
    // Set selected station
    setSelectedStation(station);
    
    // Draw route for selected station
    if (station.geometry) {
      const routeCoordinates = station.geometry.coordinates.map(coord => [coord[1], coord[0]]);
      const routeLayer = L.polyline(routeCoordinates, {
        ...ROUTE_STYLES.selected,
        lineJoin: 'round'
      }).addTo(mapInstanceRef.current);
      routeLayersRef.current.push(routeLayer);
    } else {
      const routeLayer = L.polyline(
        [[userLocation.lat, userLocation.lng], [station.lat, station.lng]],
        ROUTE_STYLES.fallback
      ).addTo(mapInstanceRef.current);
      routeLayersRef.current.push(routeLayer);
    }
    
    // Pan to show both user and station
    const bounds = L.latLngBounds(
      [userLocation.lat, userLocation.lng],
      [station.lat, station.lng]
    );
    mapInstanceRef.current.fitBounds(bounds, { padding: [50, 50] });
  }, [userLocation]);

  // Initialize Leaflet map
  useEffect(() => {
    if (!userLocation || !mapRef.current || mapInstanceRef.current) return;

    import('leaflet').then((L) => {
      // Fix Leaflet default marker icon issue
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: LEAFLET_CDN.markerIcon2x,
        iconUrl: LEAFLET_CDN.markerIcon,
        shadowUrl: LEAFLET_CDN.markerShadow,
      });

      // Create map
      const map = L.map(mapRef.current).setView(
        [userLocation.lat, userLocation.lng], 
        MAP_CONFIG.defaultZoom
      );
      mapInstanceRef.current = map;

      // Add OpenStreetMap tiles
      L.tileLayer(MAP_CONFIG.tileLayerUrl, {
        attribution: MAP_CONFIG.attribution,
        maxZoom: MAP_CONFIG.maxZoom,
      }).addTo(map);

      // Custom icon for user location
      const userIcon = L.divIcon({
        className: 'custom-user-marker',
        html: `<div style="
          width: 24px;
          height: 24px;
          background: #3b82f6;
          border: 4px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      // Add user location marker
      L.marker([userLocation.lat, userLocation.lng], { icon: userIcon })
        .addTo(map)
        .bindPopup(`
          <div style="text-align: center; padding: 8px;">
            <strong style="color: #3b82f6;">📍 Your Location</strong>
          </div>
        `);

      // Custom icon for stations
      const createStationIcon = (isNearest) => L.divIcon({
        className: 'custom-station-marker',
        html: `<div style="
          width: 36px;
          height: 36px;
          background: ${isNearest ? '#22c55e' : '#16a34a'};
          border: 3px solid white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          ${isNearest ? 'animation: pulse 2s infinite;' : ''}
        ">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
            <rect x="6" y="4" width="12" height="16" rx="2" stroke="white" stroke-width="2" fill="none"/>
            <rect x="8" y="6" width="8" height="6" fill="white"/>
            <line x1="10" y1="2" x2="10" y2="4" stroke="white" stroke-width="2"/>
            <line x1="14" y1="2" x2="14" y2="4" stroke="white" stroke-width="2"/>
          </svg>
        </div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      // Store Leaflet reference
      leafletRef.current = L;

      // Add station markers
      stationsWithDistance.forEach((station, index) => {
        const isNearest = index === 0;
        const marker = L.marker([station.lat, station.lng], { 
          icon: createStationIcon(isNearest) 
        }).addTo(map);

        marker.bindPopup(`
          <div style="padding: 12px; min-width: 200px;">
            <h3 style="margin: 0 0 8px 0; color: ${isNearest ? '#22c55e' : '#16a34a'}; font-size: 14px; font-weight: 600;">
              ${isNearest ? '⭐ NEAREST - ' : ''}${station.name}
            </h3>
            <div style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: #666;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span>🛣️ ${station.distance.toFixed(2)} km ${station.isRoadDistance ? '(by road)' : '(straight line)'}</span>
              </div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span>🔋 ${station.batteries} batteries available</span>
              </div>
            </div>
            ${isNearest ? '<p style="margin: 8px 0 0 0; font-size: 11px; color: #22c55e; font-weight: 500;">This is your nearest swap station!</p>' : ''}
          </div>
        `);

        // Show route when marker is clicked
        marker.on('click', () => {
          showRouteForStation(station);
        });
      });

      // Add CSS animation for pulsing effect
      const style = document.createElement('style');
      style.textContent = `
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
          100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
      `;
      document.head.appendChild(style);

      setMapReady(true);
    });

    // Cleanup on unmount
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [userLocation, stationsWithDistance, showRouteForStation]);

  return {
    // State
    userLocation,
    locationError,
    isLoading,
    mapReady,
    nearestStation,
    stationsWithDistance,
    routesLoading,
    selectedStation,
    // Refs
    mapRef,
    // Actions
    showRouteForStation,
  };
}
