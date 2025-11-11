'use client';

interface ForecastScheduleProps {
  data: {
    meta: {
      generated_at: string;
      location: { lat: number; lon: number };
      forecast_horizon_hours: number;
      source: string;
    };
    weather: Array<{
      time: string;
      ghi: number;
      cloud: number;
      poa_global: number;
      predicted_kW: number;
    }>;
    forecast_kW: number[];
    soc_target: number;
    schedule: Array<{
      step: number;
      time: string;
      solar_kW: number;
      load_kW: number;
      charging_kW: number;
      discharging_kW: number;
      soc_percent: number;
    }>;
  };
  location: { lat: number; lon: number };
  loading: boolean;
}

export default function ForecastSchedule({ data, location, loading }: ForecastScheduleProps) {
  // Add defensive checks for missing data
  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12 text-center">
        <p className="text-gray-600 dark:text-gray-400">No forecast data available</p>
      </div>
    );
  }

  // Safely handle forecast_kW - might be undefined or missing
  const forecast_kW = data.forecast_kW || [];
  const schedule = data.schedule || [];
  const weather = data.weather || [];
  
  const maxForecast = forecast_kW.length > 0 ? Math.max(...forecast_kW, 1) : 1;
  const maxSolar = schedule.length > 0 ? Math.max(...schedule.map(s => s.solar_kW || 0), 1) : 1;
  const maxLoad = schedule.length > 0 ? Math.max(...schedule.map(s => s.load_kW || 0), 1) : 1;

  return (
    <div className="space-y-6">
      {/* Meta Information */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors duration-300">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Location</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {location.lat.toFixed(4)}°N, {location.lon.toFixed(4)}°E
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Forecast Horizon</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {data.meta?.forecast_horizon_hours || 'N/A'} hours
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">SOC Target</div>
            <div className="text-lg font-semibold text-yellow-600">
              {data.soc_target ? (data.soc_target * 100).toFixed(0) : 'N/A'}%
            </div>
          </div>
        </div>
        <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
          Generated at: {data.meta?.generated_at ? new Date(data.meta.generated_at).toLocaleString() : 'N/A'}
        </div>
      </div>

      {/* Forecast display removed - using forecast from dashboard page */}

      {/* Schedule Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors duration-300">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Battery Schedule</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-2 px-3 text-gray-700 dark:text-gray-300">Step</th>
                <th className="text-left py-2 px-3 text-gray-700 dark:text-gray-300">Time</th>
                <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-300">Solar (kW)</th>
                <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-300">Load (kW)</th>
                <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-300">Charging (kW)</th>
                <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-300">Discharging (kW)</th>
                <th className="text-right py-2 px-3 text-gray-700 dark:text-gray-300">SOC (%)</th>
              </tr>
            </thead>
            <tbody>
              {schedule.length > 0 ? (
                schedule.map((s) => (
                  <tr
                    key={s.step}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="py-2 px-3 text-gray-900 dark:text-white font-medium">{s.step}</td>
                    <td className="py-2 px-3 text-gray-700 dark:text-gray-300">
                      {new Date(s.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="text-right py-2 px-3 text-green-600 font-semibold">{s.solar_kW.toFixed(2)}</td>
                    <td className="text-right py-2 px-3 text-gray-700 dark:text-gray-300">{s.load_kW.toFixed(2)}</td>
                    <td className="text-right py-2 px-3 text-blue-600 font-semibold">
                      {s.charging_kW > 0 ? s.charging_kW.toFixed(2) : '-'}
                    </td>
                    <td className="text-right py-2 px-3 text-red-600 font-semibold">
                      {s.discharging_kW > 0 ? s.discharging_kW.toFixed(2) : '-'}
                    </td>
                    <td className="text-right py-2 px-3">
                      <span
                        className={`font-semibold ${
                          s.soc_percent < 20
                            ? 'text-red-600'
                            : s.soc_percent < 50
                            ? 'text-yellow-600'
                            : 'text-green-600'
                        }`}
                      >
                        {Math.round(s.soc_percent)}%
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-500 dark:text-gray-400">
                    No schedule data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* SOC Trend Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors duration-300">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Battery SOC Trend</h3>
        
        {schedule.length > 0 ? (
          <>
            {/* Chart Container with Y-axis */}
            <div className="relative h-64 mb-4">
              {/* Y-axis labels */}
              <div className="absolute left-0 top-0 bottom-8 flex flex-col justify-between text-xs text-gray-500 dark:text-gray-400 pr-2">
                <span>100%</span>
                <span>75%</span>
                <span>50%</span>
                <span>25%</span>
                <span>0%</span>
              </div>
              
              {/* Chart area */}
              <div className="ml-8 h-full flex items-end justify-between gap-0.5 relative">
                {/* Target line */}
                <div 
                  className="absolute left-0 right-0 border-t-2 border-dashed border-blue-400 dark:border-blue-500 opacity-50 z-10"
                  style={{ bottom: `${(data.soc_target || 0.8) * 100}%` }}
                  title={`Target: ${((data.soc_target || 0.8) * 100).toFixed(0)}%`}
                ></div>
                
                {/* Sample data points for better visualization (show every Nth point) */}
                {(() => {
                  const sampleRate = Math.max(1, Math.floor(schedule.length / 60)); // Show max 60 points
                  const sampledSchedule = schedule.filter((_, idx) => idx % sampleRate === 0 || idx === schedule.length - 1);
                  const maxSOC = Math.max(...schedule.map(s => s.soc_percent), 100);
                  const minSOC = Math.min(...schedule.map(s => s.soc_percent), 0);
                  const range = maxSOC - minSOC || 100;
                  
                  return sampledSchedule.map((s, idx) => {
                    // Calculate height as percentage of chart height (192px = h-48)
                    const heightPercent = ((s.soc_percent - minSOC) / range) * 100;
                    const heightPx = Math.max(2, (heightPercent / 100) * 192); // Min 2px height
                    
                    return (
                      <div 
                        key={`${s.step}-${idx}`} 
                        className="flex-1 flex flex-col items-center group relative"
                        style={{ minWidth: '2px' }}
                      >
                        <div
                          className={`w-full rounded-t transition-all hover:opacity-80 ${
                            s.soc_percent < 20
                              ? 'bg-gradient-to-t from-red-500 to-red-400'
                              : s.soc_percent < 50
                              ? 'bg-gradient-to-t from-yellow-500 to-yellow-400'
                              : 'bg-gradient-to-t from-green-500 to-green-400'
                          }`}
                          style={{ height: `${heightPx}px` }}
                          title={`Step ${s.step}: ${Math.round(s.soc_percent)}%`}
                        ></div>
                        {/* Show step number on hover or for every 10th point */}
                        {(idx % 10 === 0 || idx === sampledSchedule.length - 1) && (
                          <div className="text-[10px] text-gray-500 dark:text-gray-400 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            {s.step}
                          </div>
                        )}
                      </div>
                    );
                  });
                })()}
              </div>
            </div>
            
            {/* Summary */}
            <div className="mt-4 flex items-center justify-between text-sm border-t border-gray-200 dark:border-gray-700 pt-4">
              <div className="flex items-center gap-4">
                <div className="text-gray-600 dark:text-gray-400">
                  <span className="font-semibold">Target:</span> {data.soc_target ? (data.soc_target * 100).toFixed(0) : 'N/A'}%
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  <span className="font-semibold">Start:</span> {schedule[0]?.soc_percent ? Math.round(schedule[0].soc_percent) : 'N/A'}%
                </div>
                <div className="text-gray-600 dark:text-gray-400">
                  <span className="font-semibold">End:</span> {schedule[schedule.length - 1]?.soc_percent ? Math.round(schedule[schedule.length - 1].soc_percent) : 'N/A'}%
                </div>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {schedule.length} time slots
              </div>
            </div>
          </>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
            No schedule data available
          </div>
        )}
      </div>
    </div>
  );
}

