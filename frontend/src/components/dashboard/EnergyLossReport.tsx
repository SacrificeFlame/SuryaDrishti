'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Battery, AlertTriangle, Zap } from 'lucide-react';

interface EnergyLossReportProps {
  microgridId: string;
}

interface ReportData {
  microgrid_id: string;
  period: {
    start_date: string;
    end_date: string;
  };
  metrics: {
    total_forecast_energy_kwh: number;
    total_actual_energy_kwh: number;
    energy_saved_kwh: number;
    prevented_outages: number;
    battery_cycles_saved: number;
    alerts_triggered: number;
    forecast_accuracy_percent: number;
  };
  summary: {
    total_alerts: number;
    critical_alerts: number;
    warning_alerts: number;
    actions_taken: number;
  };
}

export default function EnergyLossReport({ microgridId }: EnergyLossReportProps) {
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    fetchReport();
  }, [microgridId, days]);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      // Use environment variable for API URL
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(
        `${apiUrl}/reports/energy-loss/${microgridId}?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch report: ${response.statusText}`);
      }
      
      const data = await response.json();
      setReportData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report');
      console.error('Error fetching energy loss report:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-600 dark:text-gray-400">Loading report...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="text-center text-red-600 dark:text-red-400">Error: {error}</div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="text-center text-gray-600 dark:text-gray-400">No report data available</div>
      </div>
    );
  }

  const { metrics, summary } = reportData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Energy Loss Prevention Report</h2>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Period: {reportData.period.start_date} to {reportData.period.end_date}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Energy Saved</div>
              <div className="text-2xl font-bold text-green-600">{metrics.energy_saved_kwh.toFixed(1)} kWh</div>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Prevented Outages</div>
              <div className="text-2xl font-bold text-blue-600">{metrics.prevented_outages}</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Battery Cycles Saved</div>
              <div className="text-2xl font-bold text-yellow-600">{metrics.battery_cycles_saved.toFixed(1)}</div>
            </div>
            <Battery className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Forecast Accuracy</div>
              <div className="text-2xl font-bold text-purple-600">{metrics.forecast_accuracy_percent.toFixed(1)}%</div>
            </div>
            <Zap className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Detailed Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Forecast Energy</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.total_forecast_energy_kwh.toFixed(2)} kWh
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Actual Energy</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.total_actual_energy_kwh.toFixed(2)} kWh
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Alerts Triggered</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.alerts_triggered}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Actions Taken</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {summary.actions_taken}
            </div>
          </div>
        </div>
      </div>

      {/* Alert Summary */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Alert Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{summary.critical_alerts}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Critical Alerts</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{summary.warning_alerts}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Warning Alerts</div>
          </div>
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{summary.total_alerts}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Alerts</div>
          </div>
        </div>
      </div>
    </div>
  );
}

