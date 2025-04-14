import { FaPlus, FaTimes } from 'react-icons/fa';

export default function ConditionEditor({
  title,
  enabled,
  onToggle,
  conditions,
  onChange,
  onAdd,
  onRemove,
  COMPARATORS,
}) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <input type="checkbox" checked={enabled} onChange={onToggle} />
        <h3 className="text-lg font-semibold text-gray-200">{title}</h3>
      </div>

      {enabled && (
        <div className="space-y-3 ml-4">
          {conditions.map((condition, index) => (
            <div key={index} className="flex items-center gap-3">
              <select
                value={condition.comparator}
                onChange={(e) => onChange(index, 'comparator', e.target.value)}
                className="w-20 bg-gray-800 border border-gray-600 text-white rounded-md px-2 py-1"
              >
                {COMPARATORS.map(comp => (
                  <option key={comp} value={comp}>{comp}</option>
                ))}
              </select>
              <input
                type="number"
                value={condition.value}
                onChange={(e) => onChange(index, 'value', e.target.value)}
                className="w-28 bg-gray-800 border border-gray-600 text-white rounded-md px-3 py-1"
              />
              <button
                type="button"
                onClick={() => onRemove(index)}
                className="text-red-500 hover:text-red-300"
              >
                <FaTimes />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={onAdd}
            className="text-green-400 hover:text-green-300 flex items-center gap-2 mt-1"
          >
            <FaPlus className="text-sm" /> Add Condition
          </button>
        </div>
      )}
    </div>
  );
}
