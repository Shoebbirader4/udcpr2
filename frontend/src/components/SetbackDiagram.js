import React from 'react';

export default function SetbackDiagram({ setbackResult }) {
  if (!setbackResult) return null;

  const { front_m = 0, side_m = 0, rear_m = 0 } = setbackResult;

  return (
    <div className="space-y-4">
      <div className="relative w-full aspect-square bg-gray-100 rounded-lg p-8">
        {/* Plot boundary */}
        <div className="absolute inset-8 border-4 border-gray-400 rounded">
          {/* Building (inner rectangle) */}
          <div 
            className="absolute bg-blue-200 border-2 border-blue-600 rounded flex items-center justify-center"
            style={{
              top: `${(front_m / 10) * 100}%`,
              left: `${(side_m / 10) * 100}%`,
              right: `${(side_m / 10) * 100}%`,
              bottom: `${(rear_m / 10) * 100}%`,
            }}
          >
            <span className="text-xs font-medium text-blue-900">Building</span>
          </div>

          {/* Setback labels */}
          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-700">
            Front: {front_m}m
          </div>
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-700">
            Rear: {rear_m}m
          </div>
          <div className="absolute left-2 top-1/2 transform -translate-y-1/2 -rotate-90 text-xs font-medium text-gray-700">
            Side: {side_m}m
          </div>
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 rotate-90 text-xs font-medium text-gray-700">
            Side: {side_m}m
          </div>
        </div>

        {/* Plot label */}
        <div className="absolute top-2 left-2 text-xs font-medium text-gray-600">
          Plot Boundary
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 bg-gray-50 rounded">
          <p className="text-xs text-gray-600">Front</p>
          <p className="text-lg font-bold text-gray-900">{front_m}m</p>
        </div>
        <div className="p-2 bg-gray-50 rounded">
          <p className="text-xs text-gray-600">Side</p>
          <p className="text-lg font-bold text-gray-900">{side_m}m</p>
        </div>
        <div className="p-2 bg-gray-50 rounded">
          <p className="text-xs text-gray-600">Rear</p>
          <p className="text-lg font-bold text-gray-900">{rear_m}m</p>
        </div>
      </div>
    </div>
  );
}
