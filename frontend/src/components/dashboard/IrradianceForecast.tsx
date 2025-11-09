'use client';

import { ForecastPoint } from '@/types/forecast';
import { Sun, Zap, Gauge, TrendingUp } from 'lucide-react';

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
  // Find max value for scaling - with defensive checks
  const safeForecasts = forecasts || [];
  const maxIrradiance = safeForecasts.length > 0 
    ? Math.max(...safeForecasts.map(f => f.p90 || 0), currentIrradiance || 0, 100)
    : Math.max(currentIrradiance || 0, 100);
  const maxPower = safeForecasts.length > 0
    ? Math.max(...safeForecasts.map(f => f.power_output || 0), currentPower || 0, 1)
    : Math.max(currentPower || 0, 1);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
            <TrendingUp className="w-5 h-5 text-slate-600 dark:text-slate-400 stroke-[1.5]" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-1">Solar Irradiance Forecast</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">60-minute probabilistic forecast</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-emerald-50 dark:bg-emerald-900/20 px-3 py-1.5 rounded-lg border border-emerald-200 dark:border-emerald-800">
          <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Confidence:</span>
          <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">{(confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      {/* Current Status Cards */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-100 dark:border-blue-800/50">
          <div className="flex items-center gap-2 mb-2">
            <Sun className="w-4 h-4 text-blue-600 dark:text-blue-400 stroke-[1.5]" />
            <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Current Irradiance</div>
          </div>
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 font-mono">{currentIrradiance.toFixed(0)}</div>
          <div className="text-[10px] text-slate-400 dark:text-slate-500 font-medium mt-1">W/m²</div>
        </div>
        <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-4 border border-emerald-100 dark:border-emerald-800/50">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-emerald-600 dark:text-emerald-400 stroke-[1.5]" />
            <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Power Output</div>
          </div>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 font-mono">{currentPower.toFixed(1)}</div>
          <div className="text-[10px] text-slate-400 dark:text-slate-500 font-medium mt-1">kW</div>
        </div>
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-100 dark:border-purple-800/50">
          <div className="flex items-center gap-2 mb-2">
            <Gauge className="w-4 h-4 text-purple-600 dark:text-purple-400 stroke-[1.5]" />
            <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Capacity Factor</div>
          </div>
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 font-mono">{((currentPower / 50) * 100).toFixed(0)}%</div>
          <div className="text-[10px] text-slate-400 dark:text-slate-500 font-medium mt-1">of 50 kW</div>
        </div>
      </div>

      {/* Chart */}
      <div className="relative h-64 border border-slate-200 dark:border-slate-700 rounded-lg p-4 bg-slate-50 dark:bg-slate-950/50">
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
          {safeForecasts.length > 0 && (
            <path
              d={`
                M 0 ${200 - ((currentIrradiance || 0) / maxIrradiance) * 200}
                ${safeForecasts.map((f, i) => {
                  const x = ((i + 1) / safeForecasts.length) * 600;
                  const y = 200 - ((f.p90 || 0) / maxIrradiance) * 200;
                  return `L ${x} ${y}`;
                }).join(' ')}
                ${safeForecasts.slice().reverse().map((f, i) => {
                  const x = ((safeForecasts.length - i - 1) / safeForecasts.length) * 600;
                  const y = 200 - ((f.p10 || 0) / maxIrradiance) * 200;
                  return `L ${x} ${y}`;
                }).join(' ')}
                L 0 ${200 - ((currentIrradiance || 0) / maxIrradiance) * 200}
              `}
              fill="rgba(59, 130, 246, 0.1)"
              stroke="none"
            />
          )}

          {/* P50 line (median) */}
          {safeForecasts.length > 0 && (
            <path
              d={`
                M 0 ${200 - ((currentIrradiance || 0) / maxIrradiance) * 200}
                ${safeForecasts.map((f, i) => {
                  const x = ((i + 1) / safeForecasts.length) * 600;
                  const y = 200 - ((f.p50 || 0) / maxIrradiance) * 200;
                  return `L ${x} ${y}`;
                }).join(' ')}
              `}
              fill="none"
              stroke="#3b82f6"
              strokeWidth="3"
            />
          )}

          {/* P10 line (pessimistic) */}
          {safeForecasts.length > 0 && (
            <path
              d={`
                M 0 ${200 - ((currentIrradiance || 0) / maxIrradiance) * 200}
                ${safeForecasts.map((f, i) => {
                  const x = ((i + 1) / safeForecasts.length) * 600;
                  const y = 200 - ((f.p10 || 0) / maxIrradiance) * 200;
                  return `L ${x} ${y}`;
                }).join(' ')}
              `}
              fill="none"
              stroke="#93c5fd"
              strokeWidth="2"
              strokeDasharray="4 2"
            />
          )}

          {/* P90 line (optimistic) */}
          {safeForecasts.length > 0 && (
            <path
              d={`
                M 0 ${200 - ((currentIrradiance || 0) / maxIrradiance) * 200}
                ${safeForecasts.map((f, i) => {
                  const x = ((i + 1) / safeForecasts.length) * 600;
                  const y = 200 - ((f.p90 || 0) / maxIrradiance) * 200;
                  return `L ${x} ${y}`;
                }).join(' ')}
              `}
              fill="none"
              stroke="#1e40af"
              strokeWidth="2"
              strokeDasharray="4 2"
            />
          )}

          {/* Current point */}
          <circle
            cx="0"
            cy={200 - ((currentIrradiance || 0) / maxIrradiance) * 200}
            r="5"
            fill="#10b981"
            stroke="#fff"
            strokeWidth="2"
          />

          {/* Time labels */}
          {safeForecasts.length > 0 ? (
            safeForecasts.map((f, i) => (
              <text
                key={`time-${i}`}
                x={((i + 1) / safeForecasts.length) * 600}
                y="195"
                textAnchor="middle"
                fontSize="10"
                fill="#6b7280"
              >
                {f.time || `${((i + 1) * 10 / 60).toFixed(1)}h`}
              </text>
            ))
          ) : (
            <text
              x="300"
              y="100"
              textAnchor="middle"
              fontSize="14"
              fill="#9ca3af"
            >
              No forecast data available
            </text>
          )}
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
            {safeForecasts.length > 0 ? (
              safeForecasts.map((f, i) => (
                <tr key={i} className="border-t border-gray-100 dark:border-gray-700">
                  <td className="px-4 py-2 font-medium">{f.time || `${((i + 1) * 10 / 60).toFixed(1)}h`}</td>
                  <td className="px-4 py-2 text-right">{(f.p10 || 0).toFixed(0)}</td>
                  <td className="px-4 py-2 text-right font-bold">{(f.p50 || 0).toFixed(0)}</td>
                  <td className="px-4 py-2 text-right">{(f.p90 || 0).toFixed(0)}</td>
                  <td className="px-4 py-2 text-right text-green-600 font-medium">
                    {(f.power_output || 0).toFixed(1)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  No forecast data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

