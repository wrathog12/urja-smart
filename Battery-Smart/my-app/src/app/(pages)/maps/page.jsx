"use client";

import { MapHeader, StationsList, LoadingSpinner } from './components';
import { useMap } from './hooks';
import { LEAFLET_CDN } from './constants';

export default function MapsPage() {
  const {
    userLocation,
    locationError,
    isLoading,
    nearestStation,
    stationsWithDistance,
    routesLoading,
    selectedStation,
    mapRef,
    showRouteForStation,
  } = useMap();

  if (isLoading) {
    return <LoadingSpinner message="Getting your location..." />;
  }

  return (
    <div className="h-full w-full flex flex-col bg-gray-50">
      {/* Header */}
      <MapHeader
        routesLoading={routesLoading}
        nearestStation={nearestStation}
        locationError={locationError}
      />

      {/* Map Container */}
      <div className="flex-1 relative">
        <link
          rel="stylesheet"
          href={LEAFLET_CDN.css}
          integrity={LEAFLET_CDN.cssIntegrity}
          crossOrigin=""
        />
        <div 
          ref={mapRef} 
          className="absolute inset-0 z-0"
          style={{ background: '#e5e7eb' }}
        />
        
        {/* Stations List Overlay */}
        <StationsList
          stations={stationsWithDistance}
          selectedStation={selectedStation}
          onStationClick={showRouteForStation}
        />
      </div>
    </div>
  );
}
