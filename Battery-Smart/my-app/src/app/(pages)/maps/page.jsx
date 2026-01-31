"use client";

import { GoogleMap, Marker, TrafficLayer } from '@react-google-maps/api';
import { MapHeader, StationsList, LoadingSpinner } from './components';
import { useMap } from './hooks';
import { GOOGLE_MAPS_CONFIG, MAP_STYLES, ROUTE_STYLES, MARKER_COLORS } from './constants';

const mapContainerStyle = {
  width: '100%',
  height: '100%',
};

const mapOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  mapTypeControl: false,
  scaleControl: true,
  streetViewControl: false,
  rotateControl: false,
  fullscreenControl: true,
  styles: MAP_STYLES,
};

export default function MapsPage() {
  const {
    userLocation,
    locationError,
    isLoading,
    mapReady,
    nearestStation,
    stationsWithDistance,
    routesLoading,
    selectedStation,
    loadError,
    showTraffic,
    showRouteForStation,
    onMapLoad,
    toggleTraffic,
  } = useMap();

  if (isLoading) {
    return <LoadingSpinner message="Getting your location..." />;
  }

  if (loadError) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-gray-50">
        <div className="text-center p-8">
          <h2 className="text-xl font-semibold text-red-600 mb-2">Failed to load Google Maps</h2>
          <p className="text-gray-500">Please check your API key and try again.</p>
        </div>
      </div>
    );
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
        {mapReady && userLocation && (
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            center={userLocation}
            zoom={GOOGLE_MAPS_CONFIG.defaultZoom}
            options={mapOptions}
            onLoad={onMapLoad}
          >
            {/* User Location Marker */}
            <Marker
              position={userLocation}
              icon={{
                path: window.google?.maps?.SymbolPath?.CIRCLE || 0,
                scale: 12,
                fillColor: MARKER_COLORS.user,
                fillOpacity: 1,
                strokeColor: '#ffffff',
                strokeWeight: 4,
              }}
              title="Your Location"
            />

            {/* Station Markers */}
            {stationsWithDistance.map((station, index) => {
              const isNearest = index === 0;
              const isSelected = selectedStation?.id === station.id;
              
              return (
                <Marker
                  key={station.id}
                  position={{ lat: station.lat, lng: station.lng }}
                  onClick={() => showRouteForStation(station)}
                  icon={{
                    path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z',
                    fillColor: isNearest ? MARKER_COLORS.nearestStation : MARKER_COLORS.station,
                    fillOpacity: 1,
                    strokeColor: '#ffffff',
                    strokeWeight: 2,
                    scale: isSelected ? 2.2 : 1.8,
                    anchor: new window.google.maps.Point(12, 22),
                  }}
                  title={station.name}
                  animation={isNearest ? window.google.maps.Animation.BOUNCE : undefined}
                />
              );
            })}
            {/* Routes are drawn manually via useMap hook */}

            {/* Traffic Layer */}
            {showTraffic && <TrafficLayer />}
          </GoogleMap>
        )}

        {/* Traffic Toggle Button */}
        <button
          onClick={toggleTraffic}
          className={`absolute top-4 right-4 z-[1000] px-4 py-2 rounded-xl font-medium text-sm shadow-lg transition-all duration-200 flex items-center gap-2 ${
            showTraffic
              ? 'bg-emerald-500 text-white hover:bg-emerald-600'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
          }`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
            <circle cx="7" cy="17" r="2" />
            <path d="M9 17h6" />
            <circle cx="17" cy="17" r="2" />
          </svg>
          {showTraffic ? 'Traffic On' : 'Traffic Off'}
        </button>

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
