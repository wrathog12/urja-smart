import { Check, X } from 'lucide-react';

export default function ChargerStatus({ active, total, gridOn, backupOn }) {
  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100 w-full">
      <h2 className="text-sm font-medium text-gray-900 mb-3">Charger Status</h2>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-2xl font-semibold text-gray-900">
            {active} <span className="text-gray-400 text-lg">/ {total}</span>
          </p>
          <p className="text-xs text-gray-500">Active Chargers</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-1.5">
            {gridOn ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <X className="w-4 h-4 text-red-400" />
            )}
            <span className={`text-sm ${gridOn ? 'text-gray-600' : 'text-gray-400'}`}>Grid</span>
          </div>
          <div className="flex items-center gap-1.5">
            {backupOn ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <X className="w-4 h-4 text-red-400" />
            )}
            <span className={`text-sm ${backupOn ? 'text-gray-600' : 'text-gray-400'}`}>Backup</span>
          </div>
        </div>
      </div>
    </div>
  );
}
