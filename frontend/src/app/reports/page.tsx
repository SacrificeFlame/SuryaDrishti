'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getEnergyLossReport, getPerformanceReport } from '@/lib/api-client';
import type { EnergyLossReport, PerformanceReport } from '@/types/reports';
import { ArrowLeft, TrendingDown, Activity, AlertTriangle, Battery, Zap, DollarSign, Leaf, Download } from 'lucide-react';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function ReportsContent() {
  const { user } = useAuth();
  const [energyLossReport, setEnergyLossReport] = useState<EnergyLossReport | null>(null);
  const [performanceReport, setPerformanceReport] = useState<PerformanceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  });
  const [days, setDays] = useState(7);

  useEffect(() => {
    loadReports();
  }, [dateRange.startDate, dateRange.endDate, days]);

  const exportToCSV = (data: any, filename: string) => {
    if (!data) return;
    
    // Convert data to CSV format
    const headers: string[] = [];
    const rows: any[] = [];
    
    if (filename.includes('energy-loss')) {
      headers.push('Metric', 'Value');
      rows.push(
        ['Energy Saved (kWh)', data.metrics?.energy_saved_kwh || 0],
        ['Prevented Outages', data.metrics?.prevented_outages || 0],
        ['Battery Cycles Saved', data.metrics?.battery_cycles_saved || 0],
        ['Forecast Accuracy (%)', data.metrics?.forecast_accuracy_percent || 0],
        ['Total Alerts', data.summary?.total_alerts || 0],
        ['Critical Alerts', data.summary?.critical_alerts || 0],
        ['Actions Taken', data.summary?.actions_taken || 0],
      );
    } else if (filename.includes('performance')) {
      headers.push('Metric', 'Value');
      rows.push(
        ['Forecasts Generated', data.metrics?.forecasts_generated || 0],
        ['Sensor Readings', data.metrics?.sensor_readings || 0],
        ['System Uptime (%)', data.metrics?.system_uptime_percent || 0],
        ['Forecast Accuracy MAE', data.metrics?.forecast_accuracy_mae || 0],
        ['Critical Alerts', data.alerts_by_severity?.critical || 0],
        ['Warning Alerts', data.alerts_by_severity?.warning || 0],
        ['Info Alerts', data.alerts_by_severity?.info || 0],
      );
    }
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map((cell: any) => `"${cell}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [energyLoss, performance] = await Promise.all([
        getEnergyLossReport(DEFAULT_MICROGRID_ID, dateRange.startDate, dateRange.endDate),
        getPerformanceReport(DEFAULT_MICROGRID_ID, days),
      ]);
      
      setEnergyLossReport(energyLoss);
      setPerformanceReport(performance);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reports');
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <header className="glass border-b border-slate-200/50 dark:border-slate-800/50 sticky top-0 z-50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
            <Link href="/dashboard" className="flex items-center gap-3 group">
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-slate-50">Reports</h1>
            </Link>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-6 lg:px-8 py-8">
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto"></div>
            <p className="mt-4 text-sm text-slate-600 dark:text-slate-400">Loading reports...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="glass border-b border-slate-200/50 dark:border-slate-800/50 sticky top-0 z-50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-3 group">
              <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors" />
              <div>
                <h1 className="text-xl font-bold text-slate-900 dark:text-slate-50">Reports</h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">Energy loss and performance analytics</p>
              </div>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 lg:px-8 py-8 space-y-6">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
            <button
              onClick={loadReports}
              className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
            >
              Retry
            </button>
          </div>
        )}

        {/* Date Range Selector */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={dateRange.startDate}
                onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
              />
            </div>
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                End Date
              </label>
              <input
                type="date"
                value={dateRange.endDate}
                onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
              />
            </div>
            <div className="w-32">
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                Performance Days
              </label>
              <input
                type="number"
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value) || 7)}
                min={1}
                max={30}
                className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
              />
            </div>
          </div>
        </div>

        {/* Energy Loss Report */}
        {energyLossReport && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50">Energy Loss Prevention Report</h2>
              </div>
              <button
                onClick={() => exportToCSV(energyLossReport, 'energy-loss-report')}
                className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors text-sm font-medium"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-amber-600" />
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Energy Saved</span>
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {energyLossReport.metrics.energy_saved_kwh.toFixed(1)} kWh
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Prevented Outages</span>
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {energyLossReport.metrics.prevented_outages}
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Battery className="w-4 h-4 text-blue-500" />
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Battery Cycles Saved</span>
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {energyLossReport.metrics.battery_cycles_saved.toFixed(1)}
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-green-500" />
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Forecast Accuracy</span>
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {energyLossReport.metrics.forecast_accuracy_percent.toFixed(1)}%
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Total Alerts</p>
                <p className="text-xl font-bold text-slate-900 dark:text-slate-50">
                  {energyLossReport.summary.total_alerts}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Critical Alerts</p>
                <p className="text-xl font-bold text-red-600 dark:text-red-400">
                  {energyLossReport.summary.critical_alerts}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Actions Taken</p>
                <p className="text-xl font-bold text-green-600 dark:text-green-400">
                  {energyLossReport.summary.actions_taken}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Performance Report */}
        {performanceReport && (
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50">Performance Report</h2>
                <span className="text-sm text-slate-500 dark:text-slate-400">({performanceReport.period_days} days)</span>
              </div>
              <button
                onClick={() => exportToCSV(performanceReport, 'performance-report')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Forecasts Generated</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {performanceReport.metrics.forecasts_generated}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Sensor Readings</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {performanceReport.metrics.sensor_readings}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">System Uptime</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                  {performanceReport.metrics.system_uptime_percent.toFixed(1)}%
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Critical Alerts</p>
                <p className="text-xl font-bold text-red-600 dark:text-red-400">
                  {performanceReport.alerts_by_severity.critical}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Warning Alerts</p>
                <p className="text-xl font-bold text-amber-600 dark:text-amber-400">
                  {performanceReport.alerts_by_severity.warning}
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Info Alerts</p>
                <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                  {performanceReport.alerts_by_severity.info}
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function ReportsPage() {
  return (
    <ProtectedRoute>
      <ReportsContent />
    </ProtectedRoute>
  );
}

