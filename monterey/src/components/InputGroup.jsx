export default function InputGroup({ label, children }) {
    return (
      <div className="mb-4 flex items-center gap-4">
        <label className="w-40 text-sm text-gray-300 font-medium">{label}</label>
        {children}
      </div>
    );
  }
  