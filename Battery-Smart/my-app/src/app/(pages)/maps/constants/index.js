// Dummy Battery Smart swap stations
export const SWAP_STATIONS = [
  { id: 1, name: "Battery Smart Hub - Central", lat: 28.4270, lng: 77.1105, batteries: 12 },
  { id: 2, name: "Battery Smart Station - North", lat: 28.4248, lng: 77.0989, batteries: 8 },
  { id: 3, name: "Battery Smart Point - East", lat: 28.4234, lng: 77.1051, batteries: 15 },
  { id: 4, name: "Battery Smart Depot - South", lat: 28.4719, lng: 77.0725, batteries: 6 },
  { id: 5, name: "Battery Smart Express - West", lat: 28.4593, lng: 77.0727, batteries: 10 },
  { id: 6, name: "Battery Smart Quick Swap", lat: 28.4813, lng: 77.0930, batteries: 20 },
  { id: 7, name: "battery smart headquarter", lat: 28.4149255708546, lng: 77.08831538650755, batteries: 12 },
];

// Default location (Delhi center) - used as fallback
export const DEFAULT_LOCATION = { lat: 28.6139, lng: 77.2090 };

// Google Maps configuration
export const GOOGLE_MAPS_CONFIG = {
  apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY,
  defaultZoom: 14,
  maxZoom: 19,
  libraries: ['places', 'geometry'],
  mapId: 'battery-smart-map', // Optional: for advanced markers
};

// Map styling - dark mode friendly, clean look
export const MAP_STYLES = [
  {
    featureType: 'poi',
    elementType: 'labels',
    stylers: [{ visibility: 'off' }],
  },
  {
    featureType: 'transit',
    elementType: 'labels',
    stylers: [{ visibility: 'off' }],
  },
];

// Route styling
export const ROUTE_STYLES = {
  selected: {
    strokeColor: '#22c55e',
    strokeWeight: 5,
    strokeOpacity: 0.9,
  },
  fallback: {
    strokeColor: '#22c55e',
    strokeWeight: 4,
    strokeOpacity: 0.8,
    icons: [{
      icon: {
        path: 'M 0,-1 0,1',
        strokeOpacity: 1,
        scale: 4,
      },
      offset: '0',
      repeat: '20px',
    }],
  },
};

// Marker colors
export const MARKER_COLORS = {
  user: '#3b82f6',
  nearestStation: '#22c55e',
  station: '#16a34a',
};
