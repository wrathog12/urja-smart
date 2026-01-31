"""
Battery Smart Station Tool
Handles finding nearest battery swap stations based on location and availability.
"""
import math
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# STATIC STATION DATA (from frontend constants/index.js)
# ============================================================================
SWAP_STATIONS = [
    {"id": 1, "name": "Battery Smart Hub - Central", "lat": 28.4270, "lng": 77.1105, "batteries": 12},
    {"id": 2, "name": "Battery Smart Station - North", "lat": 28.4248, "lng": 77.0989, "batteries": 8},
    {"id": 3, "name": "Battery Smart Point - East", "lat": 28.4234, "lng": 77.1051, "batteries": 15},
    {"id": 4, "name": "Battery Smart Depot - South", "lat": 28.4719, "lng": 77.0725, "batteries": 6},
    {"id": 5, "name": "Battery Smart Express - West", "lat": 28.4593, "lng": 77.0727, "batteries": 10},
    {"id": 6, "name": "Battery Smart Quick Swap", "lat": 28.4813, "lng": 77.0930, "batteries": 20},
    {"id": 7, "name": "Battery Smart Headquarter", "lat": 28.4149, "lng": 77.0883, "batteries": 12},
]

# Default user location (Gurgaon area) - for testing
DEFAULT_USER_LOCATION = {"lat": 28.4595, "lng": 77.0266}


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(d_lat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(d_lng / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


class NearestStationTool:
    """
    Tool to find nearest battery swap stations based on location and availability.
    """
    
    def __init__(self):
        self.stations = SWAP_STATIONS
        self.default_location = DEFAULT_USER_LOCATION
    
    def find_nearest_stations(
        self, 
        user_lat: float = None, 
        user_lng: float = None, 
        min_batteries: int = 1,
        limit: int = 5
    ) -> dict:
        """
        Find the nearest stations to the user's location.
        
        Args:
            user_lat: User's latitude (uses default if None)
            user_lng: User's longitude (uses default if None)
            min_batteries: Minimum batteries required (for availability filter)
            limit: Maximum number of stations to return
        
        Returns:
            dict with:
                - speech: Hindi TTS response
                - stations: List of nearby stations with distance
                - best_station: The recommended station
                - total_nearby: Total count of nearby stations
        """
        # Use default location if not provided
        if user_lat is None:
            user_lat = self.default_location["lat"]
        if user_lng is None:
            user_lng = self.default_location["lng"]
        
        logger.info(f"📍 Finding stations near: {user_lat}, {user_lng}")
        
        # Calculate distance for each station
        stations_with_distance = []
        for station in self.stations:
            distance = haversine_distance(
                user_lat, user_lng,
                station["lat"], station["lng"]
            )
            stations_with_distance.append({
                **station,
                "distance_km": round(distance, 2)
            })
        
        # Sort by distance
        stations_with_distance.sort(key=lambda x: x["distance_km"])
        
        # Filter by availability
        available_stations = [
            s for s in stations_with_distance 
            if s["batteries"] >= min_batteries
        ]
        
        # Get top N stations
        nearby_stations = stations_with_distance[:limit]
        total_count = len(stations_with_distance)
        
        # Find best station (nearest with batteries)
        best_station = None
        nearest_station = stations_with_distance[0] if stations_with_distance else None
        
        if available_stations:
            best_station = available_stations[0]
        
        # Generate speech response
        speech = self._generate_speech(
            total_count=total_count,
            nearest_station=nearest_station,
            best_station=best_station,
            min_batteries=min_batteries
        )
        
        result = {
            "speech": speech,
            "stations": nearby_stations,
            "best_station": best_station,
            "total_nearby": total_count,
            "user_location": {"lat": user_lat, "lng": user_lng}
        }
        
        logger.info(f"🔋 Found {total_count} stations, best: {best_station['name'] if best_station else 'None'}")
        
        return result
    
    def _generate_speech(
        self, 
        total_count: int,
        nearest_station: dict,
        best_station: dict,
        min_batteries: int
    ) -> str:
        """
        Generate Hindi TTS response based on station data.
        """
        if not nearest_station:
            return "Maaf kijiye, aapke aas-paas koi station nahi mila."
        
        # Scenario 1: Nearest station has batteries - recommend it
        if best_station and nearest_station["id"] == best_station["id"]:
            distance = best_station["distance_km"]
            batteries = best_station["batteries"]
            name = best_station["name"].split(" - ")[-1] if " - " in best_station["name"] else best_station["name"]
            
            return (
                f"Main dekh rahi hu ki aapke paas {total_count} station hain. "
                f"Sabse nazdeeki {name} hai jo sirf {distance} kilometer door hai "
                f"aur wahan {batteries} battery available hain. "
                f"Kya aapko directions chahiye?"
            )
        
        # Scenario 2: Nearest station is empty, recommend next available one
        elif best_station:
            nearest_name = nearest_station["name"].split(" - ")[-1] if " - " in nearest_station["name"] else nearest_station["name"]
            best_name = best_station["name"].split(" - ")[-1] if " - " in best_station["name"] else best_station["name"]
            distance = best_station["distance_km"]
            batteries = best_station["batteries"]
            
            return (
                f"Aapke sabse paas waale {nearest_name} station pe "
                f"abhi battery available nahi hai. "
                f"Main aapko dusre station {best_name} ka raasta bata sakti hu "
                f"jo {distance} kilometer door hai aur wahan {batteries} battery available hain."
            )
        
        # Scenario 3: No stations with batteries
        else:
            return (
                f"Maaf kijiye, abhi aas-paas ke {total_count} stations mein se "
                f"kisi mein bhi battery available nahi hai. Kripya thodi der baad try karein."
            )
    
    def get_station_by_id(self, station_id: int) -> dict | None:
        """Get a specific station by ID."""
        for station in self.stations:
            if station["id"] == station_id:
                return station
        return None
    
    def get_all_stations(self) -> list:
        """Get all stations."""
        return self.stations


# Singleton instance
station_tool = NearestStationTool()
