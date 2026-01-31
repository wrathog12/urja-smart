export default function RecentSwaps({ swaps }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-50">
        <h2 className="text-sm font-medium text-gray-900">Recent Swaps</h2>
      </div>
      <div className="divide-y divide-gray-50">
        {swaps.map((swap, i) => (
          <div key={i} className="px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-400 w-12">{swap.time}</span>
              <span className="text-sm text-gray-800">{swap.batteryId}</span>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              swap.vehicle === '2W' 
                ? 'bg-blue-50 text-blue-600' 
                : 'bg-purple-50 text-purple-600'
            }`}>{swap.vehicle}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
