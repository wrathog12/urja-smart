export default function FormSection({ title, description, children }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 space-y-6">
      <div className="border-b border-gray-50 pb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && <p className="text-sm text-gray-500 mt-1">{description}</p>}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {children}
      </div>
    </div>
  );
}
