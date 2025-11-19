import React from 'react';

export default function FSIChart({ fsiResult }) {
  if (!fsiResult) return null;

  const permissible = fsiResult.permissible_fsi || 0;
  const proposed = fsiResult.proposed_fsi || 0;
  const maxValue = Math.max(permissible, proposed, 1);
  
  const permissiblePercent = (permissible / maxValue) * 100;
  const proposedPercent = (proposed / maxValue) * 100;
  const isCompliant = proposed <= permissible;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Permissible FSI</span>
          <span className="font-bold text-green-600">{permissible.toFixed(2)}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-8 relative overflow-hidden">
          <div
            className="bg-green-500 h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
            style={{ width: `${permissiblePercent}%` }}
          >
            <span className="text-xs font-medium text-white">{permissible.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Proposed FSI</span>
          <span className={`font-bold ${isCompliant ? 'text-blue-600' : 'text-red-600'}`}>
            {proposed.toFixed(2)}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-8 relative overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2 ${
              isCompliant ? 'bg-blue-500' : 'bg-red-500'
            }`}
            style={{ width: `${proposedPercent}%` }}
          >
            <span className="text-xs font-medium text-white">{proposed.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className={`p-3 rounded-lg ${isCompliant ? 'bg-green-50' : 'bg-red-50'}`}>
        <p className={`text-sm font-medium ${isCompliant ? 'text-green-900' : 'text-red-900'}`}>
          {isCompliant 
            ? `✓ Within limits (${((proposed / permissible) * 100).toFixed(1)}% utilized)`
            : `✗ Exceeds limit by ${((proposed - permissible) / permissible * 100).toFixed(1)}%`
          }
        </p>
      </div>

      {fsiResult.bonuses && fsiResult.bonuses.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm font-medium text-blue-900 mb-2">FSI Bonuses Applied:</p>
          <ul className="text-sm text-blue-800 space-y-1">
            {fsiResult.bonuses.map((bonus, idx) => (
              <li key={idx}>• {bonus.type}: +{bonus.value} FSI</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
