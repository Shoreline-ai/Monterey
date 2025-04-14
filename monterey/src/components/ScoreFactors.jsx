export default function ScoreFactors({ scoreFactors, weights, onWeightChange }) {
    return (
      <div className="space-y-3">
        {scoreFactors.map((factor, index) => (
          <div key={factor} className="flex items-center gap-4">
            <label className="w-40 text-sm text-gray-300">{factor}</label>
            <input
              type="number"
              value={weights[index]}
              onChange={(e) => onWeightChange(index, Number(e.target.value))}
              className="w-28 bg-gray-800 border border-gray-600 text-white rounded-md px-3 py-2"
            />
          </div>
        ))}
      </div>
    );
  }
  