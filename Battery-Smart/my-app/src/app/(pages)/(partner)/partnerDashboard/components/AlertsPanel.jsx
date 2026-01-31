import { AlertTriangle, ChevronRight } from 'lucide-react';

export default function AlertsPanel({ alerts }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="space-y-2 w-full">
      <h2 className="text-sm font-medium text-gray-900">Alerts</h2>
      {alerts.map((alert) => (
        <div 
          key={alert.id} 
          className={`p-3 rounded-xl border flex items-start gap-3 ${
            alert.type === 'critical' 
              ? 'bg-red-50 border-red-100' 
              : 'bg-amber-50 border-amber-100'
          }`}
        >
          <AlertTriangle className={`w-4 h-4 mt-0.5 ${
            alert.type === 'critical' ? 'text-red-500' : 'text-amber-500'
          }`} />
          <div className="flex-1">
            <p className={`text-sm ${
              alert.type === 'critical' ? 'text-red-700' : 'text-amber-700'
            }`}>{alert.message}</p>
            <p className="text-xs text-gray-400 mt-0.5">{alert.time}</p>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-300" />
        </div>
      ))}
    </div>
  );
}
