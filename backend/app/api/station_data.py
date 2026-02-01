"""
Station Data API - Receives and caches station data with ETA/traffic from frontend.
This avoids repetitive Google Maps API calls by caching the data.
"""
import time
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["station"])

# ============================================================================
# Cache Configuration
# ============================================================================
CACHE_TTL_SECONDS = 300  # 5 minutes

# In-memory cache for station data
_station_cache = {
    "data": None,
    "user_location": None,
    "timestamp": 0
}


# ============================================================================
# Pydantic Models
# ============================================================================
class StationData(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    batteries: int
    distance: float  # km (straight-line or road distance)
    duration: Optional[float] = None  # minutes (ETA with traffic)
    isRoadDistance: bool = False


class StationDataRequest(BaseModel):
    user_location: dict  # {lat: float, lng: float}
    stations: List[StationData]


class StationDataResponse(BaseModel):
    success: bool
    cached: bool
    station_count: int
    nearest_station: Optional[dict] = None  # by distance
    best_station: Optional[dict] = None  # by ETA


# ============================================================================
# API Endpoints
# ============================================================================
@router.post("/station-data", response_model=StationDataResponse)
async def receive_station_data(request: StationDataRequest):
    """
    Receive station data with ETA/traffic from frontend.
    Caches the data to avoid repetitive Google Maps API calls.
    """
    global _station_cache
    
    try:
        stations = [s.model_dump() for s in request.stations]
        
        # Sort by distance to find nearest
        stations_by_distance = sorted(stations, key=lambda x: x["distance"])
        nearest = stations_by_distance[0] if stations_by_distance else None
        
        # Sort by ETA (duration) to find best - only consider stations with valid duration
        stations_with_eta = [s for s in stations if s.get("duration") is not None]
        if stations_with_eta:
            stations_by_eta = sorted(stations_with_eta, key=lambda x: x["duration"])
            best = stations_by_eta[0]
        else:
            # Fallback to nearest if no ETA data
            best = nearest
        
        # Cache the data
        _station_cache = {
            "data": stations,
            "user_location": request.user_location,
            "timestamp": time.time(),
            "nearest": nearest,
            "best": best
        }
        
        logger.info(f"📍 Cached {len(stations)} stations. Nearest: {nearest['name'] if nearest else 'None'}, Best: {best['name'] if best else 'None'}")
        
        return StationDataResponse(
            success=True,
            cached=True,
            station_count=len(stations),
            nearest_station=nearest,
            best_station=best
        )
    
    except Exception as e:
        logger.error(f"Error caching station data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/station-data")
async def get_station_data():
    """
    Get cached station data.
    """
    global _station_cache
    
    # Check if cache is valid
    if _station_cache["data"] is None:
        return {
            "success": False,
            "cached": False,
            "message": "No station data cached. Frontend needs to send data first."
        }
    
    # Check if cache is expired
    age = time.time() - _station_cache["timestamp"]
    if age > CACHE_TTL_SECONDS:
        return {
            "success": False,
            "cached": False,
            "message": f"Cache expired ({age:.0f}s old). Frontend needs to refresh data."
        }
    
    return {
        "success": True,
        "cached": True,
        "age_seconds": age,
        "user_location": _station_cache["user_location"],
        "stations": _station_cache["data"],
        "nearest_station": _station_cache.get("nearest"),
        "best_station": _station_cache.get("best")
    }


# ============================================================================
# Helper Functions (for use by battery.py tool)
# ============================================================================
def get_cached_stations():
    """Get cached station data for use by battery tool."""
    global _station_cache
    
    if _station_cache["data"] is None:
        return None
    
    age = time.time() - _station_cache["timestamp"]
    if age > CACHE_TTL_SECONDS:
        return None
    
    return _station_cache


def get_nearest_station():
    """Get the nearest station (by distance)."""
    cache = get_cached_stations()
    if cache:
        return cache.get("nearest")
    return None


def get_best_station():
    """Get the best station (by ETA)."""
    cache = get_cached_stations()
    if cache:
        return cache.get("best")
    return None
