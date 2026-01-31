export default function StatusBar({ label, count, total, color, icon: Icon }) {
  const percentage = (count / total) * 100;
  
  return (
    <div className="flex items-center gap-3">
      <div className="w-20 text-sm text-gray-600 flex items-center gap-1.5">
        {Icon && <Icon className="w-3.5 h-3.5" />}
        {label}
      </div>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="w-8 text-sm text-gray-800 text-right">{count}</span>
    </div>
  );
}
