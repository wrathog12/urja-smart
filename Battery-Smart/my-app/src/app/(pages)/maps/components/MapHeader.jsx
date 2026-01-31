import { MapPin, Navigation, AlertCircle, Loader2 } from 'lucide-react';

export default function MapHeader({ routesLoading, nearestStation, locationError }) {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
            <MapPin className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-800">Battery Swap Stations</h1>
            <p className="text-sm text-gray-500">Find the nearest swap station</p>
          </div>
        </div>
        
        {routesLoading ? (
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-xl border border-gray-200">
            <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />
            <span className="text-sm font-medium text-gray-500">
              Calculating distances...
            </span>
          </div>
        ) : nearestStation && (
          <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 rounded-xl border border-emerald-200">
            <Navigation className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-medium text-emerald-700">
              Nearest: {nearestStation.distance.toFixed(2)} km
            </span>
          </div>
        )}
      </div>
      
      {locationError && (
        <div className="mt-3 flex items-center gap-2 text-orange-600 text-sm">
          <AlertCircle className="w-4 h-4" />
          {locationError}
        </div>
      )}
    </div>
  );
}
