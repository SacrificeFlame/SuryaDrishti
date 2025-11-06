'use client';

import { ForecastPoint } from '@/types/forecast';

interface IrradianceForecastProps {
  forecasts: ForecastPoint[];
  currentIrradiance: number;
  currentPower: number;
  confidence: number;
}

export default function IrradianceForecast({
  forecasts,
  currentIrradiance,
  currentPower,
  confidence
}: IrradianceForecastProps) {
  // Find max value for scaling
  const maxIrradiance = Math.max(...forecasts.map(f => f.p90), currentIrradiance);
  const maxPower = Math.max(...forecasts.map(f => f.power_output), currentPower);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors duration-300">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Solar Irradiance Forecast</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">Confidence:</span>
          <span className="text-lg font-bold text-green-600">{(confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Current Status Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Current Irradiance</div>
          <div className="text-2xl font-bold text-blue-600">{currentIrradiance.toFixed(0)}</div>
          <div className="text-xs text-gray-500">W/m²</div>
        </div>
        <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Power Output</div>
          <div className="text-2xl font-bold text-green-600">{currentPower.toFixed(1)}</div>
          <div className="text-xs text-gray-500">kW</div>
        </div>
        <div className="bg-purple-50 dark:bg-purple-900/30 rounded-lg p-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Capacity Factor</div>
          <div className="text-2xl font-bold text-purple-600">{((currentPower / 50) * 100).toFixed(0)}%</div>
          <div className="text-xs text-gray-500">of 50 kW</div>
        </div>
      </div>

      {/* Chart */}
      <div className="relative h-64 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
        <svg width="100%" height="100%" viewBox="0 0 600 200">
          {/* Grid lines */}
          {[0, 1, 2, 3, 4].map(i => (
            <line
              key={`grid-${i}`}
              x1="0"
              y1={i * 50}
              x2="600"
              y2={i * 50}
              stroke="currentColor"
              className="text-gray-300 dark:text-gray-700"
              strokeWidth="1"
            />
          ))}

          {/* P10-P90 confidence band */}
          <path
            d={`
              M 0 ${200 - (currentIrradiance / maxIrradiance) * 200}
              ${forecasts.map((f, i) => {
                const x = ((i + 1) / forecasts.length) * 600;
                const y = 200 - (f.p90 / maxIrradiance) * 200;
                return `L ${x} ${y}`;
              }).join(' ')}
              ${forecasts.slice().reverse().map((f, i) => {
                const x = ((forecasts.length - i - 1) / forecasts.length) * 600;
                const y = 200 - (f.p10 / maxIrradiance) * 200;
                return `L ${x} ${y}`;
              }).join(' ')}
              L 0 ${200 - (currentIrradiance / maxIrradiance) * 200}
            `}
            fill="rgba(59, 130, 246, 0.1)"
            stroke="none"
          />

          {/* P50 line (median) */}
          <path
            d={`
              M 0 ${200 - (currentIrradiance / maxIrradiance) * 200}
              ${forecasts.map((f, i) => {
                const x = ((i + 1) / forecasts.length) * 600;
                const y = 200 - (f.p50 / maxIrradiance) * 200;
                return `L ${x} ${y}`;
              }).join(' ')}
            `}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="3"
          />

          {/* P10 line (pessimistic) */}
          <path
            d={`
              M 0 ${200 - (currentIrradiance / maxIrradiance) * 200}
              ${forecasts.map((f, i) => {
                const x = ((i + 1) / forecasts.length) * 600;
                const y = 200 - (f.p10 / maxIrradiance) * 200;
                return `L ${x} ${y}`;
              }).join(' ')}
            `}
            fill="none"
            stroke="#93c5fd"
            strokeWidth="2"
            strokeDasharray="4 2"
          />

          {/* P90 line (optimistic) */}
          <path
            d={`
              M 0 ${200 - (currentIrradiance / maxIrradiance) * 200}
              ${forecasts.map((f, i) => {
                const x = ((i + 1) / forecasts.length) * 600;
                const y = 200 - (f.p90 / maxIrradiance) * 200;
                return `L ${x} ${y}`;
              }).join(' ')}
            `}
            fill="none"
            stroke="#1e40af"
            strokeWidth="2"
            strokeDasharray="4 2"
          />

          {/* Current point */}
          <circle
            cx="0"
            cy={200 - (currentIrradiance / maxIrradiance) * 200}
            r="5"
            fill="#10b981"
            stroke="#fff"
            strokeWidth="2"
          />

          {/* Time labels */}
          {forecasts.map((f, i) => (
            <text
              key={`time-${i}`}
              x={((i + 1) / forecasts.length) * 600}
              y="195"
              textAnchor="middle"
              fontSize="10"
              fill="#6b7280"
            >
              {f.time}
            </text>
          ))}
        </svg>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-blue-500"></div>
          <span>P50 (Most Likely)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-blue-300 border-dashed"></div>
          <span>P10 (Pessimistic)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 bg-blue-800 border-dashed"></div>
          <span>P90 (Optimistic)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-4 bg-blue-100"></div>
          <span>Confidence Band</span>
        </div>
      </div>

      {/* Forecast Table */}
      <div className="mt-6 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-4 py-2 text-left">Time</th>
              <th className="px-4 py-2 text-right">P10</th>
              <th className="px-4 py-2 text-right">P50</th>
              <th className="px-4 py-2 text-right">P90</th>
              <th className="px-4 py-2 text-right">Power (kW)</th>
            </tr>
          </thead>
          <tbody>
            {forecasts.map((f, i) => (
              <tr key={i} className="border-t border-gray-100 dark:border-gray-700">
                <td className="px-4 py-2 font-medium">{f.time}</td>
                <td className="px-4 py-2 text-right">{f.p10.toFixed(0)}</td>
                <td className="px-4 py-2 text-right font-bold">{f.p50.toFixed(0)}</td>
                <td className="px-4 py-2 text-right">{f.p90.toFixed(0)}</td>
                <td className="px-4 py-2 text-right text-green-600 font-medium">
                  {f.power_output.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

