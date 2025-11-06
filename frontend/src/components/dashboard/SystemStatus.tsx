'use client';

import { SystemStatus as SystemStatusType } from '@/types/forecast';

interface SystemStatusProps {
  status: SystemStatusType;
}

export default function SystemStatus({ status }: SystemStatusProps) {
  const getStatusColor = (dieselStatus: string) => {
    switch (dieselStatus) {
      case 'running':
        return 'text-green-600 bg-green-100';
      case 'standby':
        return 'text-yellow-600 bg-yellow-100';
      case 'off':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getBatteryColor = (soc: number) => {
    if (soc >= 80) return 'text-green-600';
    if (soc >= 50) return 'text-yellow-600';
    if (soc >= 20) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-6">System Status</h2>

      {/* Battery SOC Gauge */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Battery State of Charge</span>
          <span className={`text-2xl font-bold ${getBatteryColor(status.battery_soc)}`}>
            {status.battery_soc}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
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
          <span className="text-sm font-medium text-gray-700">Diesel Generator</span>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold uppercase ${getStatusColor(
              status.diesel_status
            )}`}
          >
            {status.diesel_status}
          </span>
        </div>
      </div>

      {/* Load Distribution */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Power Distribution</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Solar Generation</span>
              <span className="font-bold text-green-600">{status.solar_generation_kw.toFixed(1)} kW</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-full rounded-full"
                style={{ width: `${(status.solar_generation_kw / 50) * 100}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Load</span>
              <span className="font-bold text-blue-600">{status.load_kw.toFixed(1)} kW</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-full rounded-full"
                style={{ width: `${(status.load_kw / 50) * 100}%` }}
              ></div>
            </div>
          </div>

          {status.grid_import_kw > 0 && (
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Grid Import</span>
                <span className="font-bold text-purple-600">{status.grid_import_kw.toFixed(1)} kW</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
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
      <div className="pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">System Uptime</span>
          <span className="text-lg font-bold text-gray-900">
            {Math.floor(status.uptime_hours / 24)}d {status.uptime_hours % 24}h
          </span>
        </div>
      </div>
    </div>
  );
}

