import { Battery, MapPin, Zap, Navigation, ChevronRight } from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';

// Generate random battery count between 0 and 15
const getRandomBatteryCount = () => Math.floor(Math.random() * 16);

// Get battery status color based on availability
const getBatteryStatus = (count) => {
  if (count === 0) return { color: 'text-red-500', bg: 'bg-red-500' };
  if (count <= 5) return { color: 'text-orange-500', bg: 'bg-orange-500' };
  if (count <= 10) return { color: 'text-yellow-500', bg: 'bg-yellow-500' };
  return { color: 'text-emerald-500', bg: 'bg-emerald-500' };
};

export default function StationsList({ 
  stations, 
  selectedStation, 
  onStationClick 
}) {
  // State to track battery counts for each station
  const [batteryCountsMap, setBatteryCountsMap] = useState({});

  // Initialize battery counts when stations change
  useEffect(() => {
    const initialCounts = {};
    stations.forEach(station => {
      initialCounts[station.id] = getRandomBatteryCount();
    });
    setBatteryCountsMap(initialCounts);
  }, [stations]);

  // Update one random station's battery every 30 seconds
  useEffect(() => {
    if (stations.length === 0) return;

    const interval = setInterval(() => {
      const randomIndex = Math.floor(Math.random() * stations.length);
      const stationToUpdate = stations[randomIndex];
      
      setBatteryCountsMap(prev => ({
        ...prev,
        [stationToUpdate.id]: getRandomBatteryCount()
      }));
    }, 30000);

    return () => clearInterval(interval);
  }, [stations]);

  const getBatteryCount = useCallback((stationId) => {
    return batteryCountsMap[stationId] ?? 0;
  }, [batteryCountsMap]);

  return (
    <div className="absolute bottom-4 left-4 right-4 md:left-4 md:right-auto md:w-96 z-[1000]">
      {/* Glassmorphism container */}
      <div 
        className="rounded-2xl shadow-2xl max-h-80 overflow-hidden"
        style={{
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.7)',
        }}
      >
        {/* Header */}
        <div 
          className="p-4 sticky top-0 z-10"
          style={{
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%)',
            borderBottom: '1px solid rgba(34, 197, 94, 0.2)',
          }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div 
                className="p-2.5 rounded-xl"
                style={{
                  background: 'linear-gradient(135deg, #22c55e 0%, #10b981 100%)',
                  boxShadow: '0 4px 14px rgba(34, 197, 94, 0.4)',
                }}
              >
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800 text-base">Nearby Stations</h3>
                <p className="text-xs text-gray-500">{stations.length} stations found</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100/80 text-emerald-700 text-xs font-semibold">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              Live
            </div>
          </div>
        </div>

        {/* Stations list */}
        <div className="overflow-y-auto max-h-56 p-2 space-y-2">
          {stations.map((station, index) => (
            <StationItem
              key={station.id}
              station={station}
              batteryCount={getBatteryCount(station.id)}
              isNearest={index === 0}
              isSelected={selectedStation?.id === station.id}
              onClick={() => onStationClick(station)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function StationItem({ station, batteryCount, isNearest, isSelected, onClick }) {
  const batteryStatus = getBatteryStatus(batteryCount);
  const batteryPercentage = (batteryCount / 15) * 100;

  return (
    <div 
      className={`
        relative p-3 rounded-xl cursor-pointer transition-all duration-200
        hover:scale-[1.01] hover:shadow-md
        ${isSelected 
          ? 'bg-gradient-to-r from-emerald-50 to-green-50 ring-2 ring-emerald-400 shadow-md' 
          : isNearest 
            ? 'bg-emerald-50/70' 
            : 'bg-white/70 hover:bg-white'
        }
      `}
      style={{ border: isSelected ? 'none' : '1px solid rgba(229, 231, 235, 0.6)' }}
      onClick={onClick}
    >
      {/* Nearest badge */}
      {isNearest && (
        <div 
          className="absolute -top-1.5 -right-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold text-white shadow-md"
          style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)' }}
        >
          ⭐ NEAREST
        </div>
      )}

      <div className="flex items-center gap-3">
        {/* Icon */}
        <div className={`
          w-11 h-11 rounded-xl flex items-center justify-center transition-all
          ${isSelected ? 'bg-emerald-500 shadow-lg shadow-emerald-200' : 'bg-gray-100'}
        `}>
          <Battery className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-gray-600'}`} />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-gray-800 truncate">
              {station.name.replace('Battery Smart ', '')}
            </span>
            {isSelected && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500 text-white">
                ACTIVE
              </span>
            )}
          </div>

          {/* Distance */}
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
            <Navigation className="w-3 h-3" />
            {station.distance.toFixed(1)} km
          </div>

          {/* Battery bar */}
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-700 ${batteryStatus.bg}`}
                style={{ width: `${batteryPercentage}%` }}
              />
            </div>
            <span className={`text-xs font-bold ${batteryStatus.color}`}>
              {batteryCount}/15
            </span>
          </div>
        </div>

        <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-emerald-500' : 'text-gray-300'}`} />
      </div>
    </div>
  );
}
