"""
Battery Smart Station Tool
Handles finding nearest battery swap stations based on location and availability.

USES ONLY CACHED DATA FROM FRONTEND - No hardcoded station data.
Frontend sends station data with ETA/traffic on page load via POST /api/station-data

- Nearest = Based on distance (km)
- Best = Based on ETA (traffic-aware travel time)
"""
import logging

logger = logging.getLogger(__name__)


class NearestStationTool:
    """
    Tool to find nearest and best battery swap stations.
    Uses cached data from frontend (no hardcoded stations).
    
    - Nearest = Based on distance (km)
    - Best = Based on ETA (traffic-aware travel time)
    """
    
    def _get_cached_data(self):
        """Get cached station data from the API module."""
        try:
            from backend.app.api.station_data import get_cached_stations
            return get_cached_stations()
        except Exception as e:
            logger.warning(f"Could not get cached data: {e}")
            return None
    
    def find_nearest_stations(
        self, 
        min_batteries: int = 1,
        limit: int = 5
    ) -> dict:
        """
        Find the nearest and best stations using cached frontend data.
        
        - Nearest = Station with smallest distance (km)
        - Best = Station with smallest ETA (traffic-aware)
        
        Args:
            min_batteries: Minimum batteries required (for availability filter)
            limit: Maximum number of stations to return
        
        Returns:
            dict with:
                - speech: Hindi TTS response
                - stations: List of nearby stations with distance/ETA
                - nearest_station: Station with smallest distance
                - best_station: Station with smallest ETA
                - total_nearby: Total count of nearby stations
        """
        # Get cached data from frontend
        cached = self._get_cached_data()
        
        if not cached or not cached.get("data"):
            logger.warning("📍 No cached station data from frontend!")
            return {
                "speech": "Maaf kijiye, station ka data abhi load nahi hua hai. Kripya thodi der baad try karein.",
                "stations": [],
                "nearest_station": None,
                "best_station": None,
                "total_nearby": 0,
                "has_eta_data": False,
                "error": "no_cached_data"
            }
        
        logger.info("📍 Using cached station data from frontend")
        
        stations = cached.get("data", [])
        user_location = cached.get("user_location", {})
        
        # Convert to our format
        stations_formatted = []
        for s in stations:
            stations_formatted.append({
                "id": s["id"],
                "name": s["name"],
                "lat": s["lat"],
                "lng": s["lng"],
                "batteries": s.get("batteries", 0),
                "distance_km": round(s.get("distance", 0), 2),
                "eta_minutes": round(s.get("duration", 0), 1) if s.get("duration") else None,
                "has_eta": s.get("duration") is not None
            })
        
        # Sort by distance for nearest
        stations_by_distance = sorted(stations_formatted, key=lambda x: x["distance_km"])
        nearest_station = stations_by_distance[0] if stations_by_distance else None
        
        # Sort by ETA for best (only stations with batteries and valid ETA)
        available_with_eta = [
            s for s in stations_formatted 
            if s["batteries"] >= min_batteries and s.get("eta_minutes") is not None
        ]
        available_by_distance = [
            s for s in stations_by_distance 
            if s["batteries"] >= min_batteries
        ]
        
        if available_with_eta:
            # Best = lowest ETA among stations with batteries
            best_station = sorted(available_with_eta, key=lambda x: x["eta_minutes"])[0]
        elif available_by_distance:
            # Fallback: nearest with batteries
            best_station = available_by_distance[0]
        else:
            best_station = None
        
        total_count = len(stations_formatted)
        nearby_stations = stations_by_distance[:limit]
        
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
            "nearest_station": nearest_station,
            "best_station": best_station,
            "total_nearby": total_count,
            "user_location": user_location,
            "has_eta_data": True
        }
        
        logger.info(f"🔋 Found {total_count} stations. Nearest: {nearest_station['name'] if nearest_station else 'None'}, Best (by ETA): {best_station['name'] if best_station else 'None'}")
        
        return result
    
    def _generate_speech(
        self, 
        total_count: int,
        nearest_station: dict,
        best_station: dict,
        min_batteries: int
    ) -> str:
        """Generate Hindi TTS response with ETA information."""
        if not nearest_station:
            return "Maaf kijiye, aapke aas-paas koi station nahi mila."
        
        def get_short_name(name):
            return name.split(" - ")[-1] if " - " in name else name
        
        nearest_name = get_short_name(nearest_station["name"])
        nearest_distance = nearest_station["distance_km"]
        
        # If best station exists and has ETA
        if best_station and best_station.get("eta_minutes"):
            best_name = get_short_name(best_station["name"])
            best_eta = int(best_station["eta_minutes"])
            best_batteries = best_station["batteries"]
            
            # If nearest and best are the same
            if nearest_station["id"] == best_station["id"]:
                return (
                    f"Main dekh rahi hu ki aapke paas {total_count} station hain. "
                    f"Sabse nazdeeki aur best option {best_name} hai "
                    f"jo sirf {best_eta} minute door hai "
                    f"aur wahan {best_batteries} battery available hain. "
                    f"Kya aapko directions chahiye?"
                )
            else:
                # Nearest and best are different
                nearest_eta = int(nearest_station["eta_minutes"]) if nearest_station.get("eta_minutes") else None
                if nearest_eta:
                    return (
                        f"Aapke sabse paas waala station {nearest_name} hai jo {nearest_eta} minute door hai, "
                        f"lekin traffic ke hisaab se best option {best_name} hai "
                        f"jo {best_eta} minute mein pahunch sakte hain "
                        f"aur wahan {best_batteries} battery available hain."
                    )
                else:
                    return (
                        f"Sabse nazdeeki station {nearest_name} hai jo {nearest_distance} km door hai. "
                        f"Lekin best option {best_name} hai "
                        f"jo {best_eta} minute mein pahunch sakte hain "
                        f"aur wahan {best_batteries} battery available hain."
                    )
        
        # Best station exists but no ETA
        elif best_station:
            best_name = get_short_name(best_station["name"])
            best_distance = best_station["distance_km"]
            best_batteries = best_station["batteries"]
            
            return (
                f"Aapke paas {total_count} station hain. "
                f"Best option {best_name} hai jo {best_distance} km door hai "
                f"aur wahan {best_batteries} battery available hain."
            )
        
        # No stations with batteries
        else:
            return (
                f"Maaf kijiye, abhi aas-paas ke {total_count} stations mein se "
                f"kisi mein bhi battery available nahi hai. Kripya thodi der baad try karein."
            )
    
    def get_all_stations(self) -> list:
        """Get all stations from cached data."""
        cached = self._get_cached_data()
        if cached:
            return cached.get("data", [])
        return []


# Singleton instance
station_tool = NearestStationTool()
