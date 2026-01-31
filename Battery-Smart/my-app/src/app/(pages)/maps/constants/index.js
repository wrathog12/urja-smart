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

// Map configuration
export const MAP_CONFIG = {
  defaultZoom: 14,
  maxZoom: 19,
  tileLayerUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
};

// OSRM API configuration
export const OSRM_CONFIG = {
  baseUrl: 'https://router.project-osrm.org/route/v1/driving',
  profile: 'driving',
};

// Leaflet CDN URLs
export const LEAFLET_CDN = {
  css: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css',
  cssIntegrity: 'sha512-Zcn6bjR/8RZbLEpLIeOwNtzREBAJnUKESxces60Mpoj+2okopSAcSUIUOseddDm0cxnGQzxIR7vJgsLZbdLE3w==',
  markerIcon: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  markerIcon2x: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  markerShadow: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
};

// Route styling
export const ROUTE_STYLES = {
  selected: {
    color: '#22c55e',
    weight: 5,
    opacity: 0.9,
  },
  fallback: {
    color: '#22c55e',
    weight: 4,
    dashArray: '10, 10',
    opacity: 0.8,
  },
};
