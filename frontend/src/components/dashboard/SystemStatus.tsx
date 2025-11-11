'use client';

import { useState } from 'react';
import { SystemStatus as SystemStatusType } from '@/types/forecast';
import { Battery, Zap, Sun, Activity, Clock, Power } from 'lucide-react';
import { getApiUrl } from '@/lib/get-api-url';

interface SystemStatusProps {
  status: SystemStatusType;
  microgridId?: string;
  onStatusUpdate?: () => void;
}

export default function SystemStatus({ status, microgridId = 'microgrid_001', onStatusUpdate }: SystemStatusProps) {
  const [toggling, setToggling] = useState(false);
  
  const handleToggleGenerator = async () => {
    if (toggling) return;
    
    const newStatus = status.diesel_status === 'off' || status.diesel_status === 'standby' ? 'on' : 'off';
    
    setToggling(true);
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/microgrid/${microgridId}/status/diesel?status=${newStatus}`, {
        method: 'PUT',
      });
      
      if (!response.ok) {
        throw new Error('Failed to update generator status');
      }
      
      // Refresh status - wait a bit for backend to update
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Refresh status
      if (onStatusUpdate) {
        onStatusUpdate();
      } else {
        // Try to reload status without full page reload
        try {
          const refreshResponse = await fetch(`${apiUrl}/microgrid/${microgridId}/status`);
          if (refreshResponse.ok) {
            const newStatus = await refreshResponse.json();
            // Update local state if possible, otherwise reload
            window.location.reload();
          } else {
            window.location.reload();
          }
        } catch {
          window.location.reload();
        }
      }
    } catch (error) {
      console.error('Failed to toggle generator:', error);
      alert('Failed to toggle generator. Please try again.');
    } finally {
      setToggling(false);
    }
  };
  
  const getStatusColor = (dieselStatus: string) => {
    switch (dieselStatus) {
      case 'running':
        return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30';
      case 'standby':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/30';
      case 'off':
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700';
    }
  };

  const getBatteryColor = (soc: number) => {
    if (soc >= 80) return 'text-green-600 dark:text-green-400';
    if (soc >= 50) return 'text-yellow-600 dark:text-yellow-400';
    if (soc >= 20) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 card-hover">
      <div className="mb-6">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-1">System Status</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400">Real-time system metrics</p>
      </div>

      {/* Battery SOC Gauge */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
              <Battery className={`w-4 h-4 ${getBatteryColor(status.battery_soc)} stroke-[1.5]`} />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Battery State of Charge</span>
          </div>
          <span className={`text-2xl font-bold ${getBatteryColor(status.battery_soc)}`}>
            {Math.round(status.battery_soc)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              status.battery_soc >= 80
                ? 'bg-green-500'
                : status.battery_soc >= 50
                ? 'bg-yellow-500'
                : status.battery_soc >= 20
                ? 'bg-orange-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${status.battery_soc}%` }}
          ></div>
        </div>
      </div>

      {/* Diesel Status */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
              <Zap className="w-4 h-4 text-slate-600 dark:text-slate-400 stroke-[1.5]" />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Diesel Generator</span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`px-3 py-1 rounded-lg text-xs font-semibold uppercase border ${getStatusColor(
                status.diesel_status
              )}`}
            >
              {status.diesel_status}
            </span>
            <button
              onClick={handleToggleGenerator}
              disabled={toggling}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                status.diesel_status === 'off' || status.diesel_status === 'standby'
                  ? 'bg-green-600 hover:bg-green-700 text-white'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <Power className="w-3 h-3" />
              {toggling ? '...' : status.diesel_status === 'off' || status.diesel_status === 'standby' ? 'Turn On' : 'Turn Off'}
            </button>
          </div>
        </div>
      </div>

      {/* Load Distribution */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
            <Activity className="w-4 h-4 text-slate-600 dark:text-slate-400 stroke-[1.5]" />
          </div>
          <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">Power Distribution</h3>
        </div>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <div className="flex items-center gap-2">
                <Sun className="w-4 h-4 text-emerald-600 dark:text-emerald-400 stroke-[1.5]" />
                <span className="text-slate-600 dark:text-slate-400">Solar Generation</span>
              </div>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">{status.solar_generation_kw.toFixed(1)} kW</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-500 h-full rounded-full"
                style={{ width: `${(status.solar_generation_kw / 50) * 100}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Load</span>
              <span className="font-bold text-blue-600 dark:text-blue-400">{status.load_kw.toFixed(1)} kW</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-full rounded-full"
                style={{ width: `${(status.load_kw / 50) * 100}%` }}
              ></div>
            </div>
          </div>

          {status.grid_import_kw > 0 && (
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600 dark:text-gray-400">Grid Import</span>
                <span className="font-bold text-purple-600 dark:text-purple-400">{status.grid_import_kw.toFixed(1)} kW</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-purple-500 h-full rounded-full"
                  style={{ width: `${(status.grid_import_kw / 50) * 100}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Uptime */}
      <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
              <Clock className="w-4 h-4 text-slate-600 dark:text-slate-400 stroke-[1.5]" />
            </div>
            <span className="text-sm text-slate-600 dark:text-slate-400">System Uptime</span>
          </div>
          <span className="text-lg font-bold text-slate-900 dark:text-slate-50">
            {(() => {
              const days = Math.floor(status.uptime_hours / 24);
              const hours = Math.floor(status.uptime_hours % 24);
              if (days > 0 && hours > 0) {
                return `${days}d ${hours}h`;
              } else if (days > 0) {
                return `${days}d`;
              } else {
                return `${hours}h`;
              }
            })()}
          </span>
        </div>
      </div>
    </div>
  );
}

