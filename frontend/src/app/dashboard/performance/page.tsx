'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardSidebar from '@/components/dashboard/DashboardSidebar';
import PerformanceMetrics from '@/components/dashboard/PerformanceMetrics';
import ThemeToggle from '@/components/ThemeToggle';
import { ArrowLeft, RefreshCw, TrendingUp, Download } from 'lucide-react';
import { getSystemStatus, getSensorHistory, getPerformanceReport } from '@/lib/api-client';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function PerformanceContent() {
  const { user } = useAuth();
  const [performanceMetrics, setPerformanceMetrics] = useState({
    dieselSavings: 0,
    forecastAccuracy: 0,
    uptime: 0,
    co2Avoided: 0
  });
  const [performanceReport, setPerformanceReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPerformance();
    const interval = setInterval(loadPerformance, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const loadPerformance = async () => {
    try {
      const [statusResponse, sensorHistory, perfReport] = await Promise.allSettled([
        getSystemStatus(DEFAULT_MICROGRID_ID),
        getSensorHistory(DEFAULT_MICROGRID_ID, 100),
        getPerformanceReport(DEFAULT_MICROGRID_ID, 7),
      ]);

      // Calculate metrics
      if (sensorHistory.status === 'fulfilled' && sensorHistory.value.length > 0) {
        const history = sensorHistory.value;
        const todayReadings = history.filter((r) => {
          const readingDate = new Date(r.timestamp);
          const today = new Date();
          return readingDate.toDateString() === today.toDateString();
        });

        const totalEnergyToday = todayReadings.reduce((sum, r) => {
          return sum + (r.power_output * 0.25);
        }, 0);
        const dieselSavings = (totalEnergyToday * 0.25 * 80);
        const co2Avoided = totalEnergyToday * 0.5;

        let forecastAccuracy = 87.5;
        if (perfReport.status === 'fulfilled' && perfReport.value?.metrics?.forecast_accuracy_mae) {
          forecastAccuracy = Math.max(70, Math.min(100, 100 - (perfReport.value.metrics.forecast_accuracy_mae * 0.5)));
        }

        const uptime = statusResponse.status === 'fulfilled' && statusResponse.value.uptime_hours
          ? Math.min(100, (statusResponse.value.uptime_hours / (30 * 24)) * 100)
          : 99.2;

        setPerformanceMetrics({
          dieselSavings,
          forecastAccuracy,
          uptime,
          co2Avoided,
        });

        if (perfReport.status === 'fulfilled') {
          setPerformanceReport(perfReport.value);
        }
      }
    } catch (err) {
      console.error('Error loading performance data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPerformance();
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex">
      <DashboardSidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5" />
                  <span className="text-sm font-medium">Back to Dashboard</span>
                </Link>
                <div className="h-6 w-px bg-slate-300 dark:bg-slate-700" />
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">Performance Analytics</h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      System performance metrics and insights
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
                <ThemeToggle />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                  <p className="mt-4 text-slate-600 dark:text-slate-400">Loading performance data...</p>
                </div>
              </div>
            ) : (
              <>
                <PerformanceMetrics metrics={performanceMetrics} />
                
                {performanceReport && (
                  <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg p-6">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-slate-50 mb-4">Detailed Performance Report</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                        <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Forecasts Generated</div>
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                          {performanceReport.metrics?.forecasts_generated || 0}
                        </div>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                        <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Sensor Readings</div>
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                          {performanceReport.metrics?.sensor_readings || 0}
                        </div>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                        <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Alerts Triggered</div>
                        <div className="text-2xl font-bold text-slate-900 dark:text-slate-50">
                          {performanceReport.metrics?.alerts_triggered || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function PerformancePage() {
  return (
    <ProtectedRoute>
      <PerformanceContent />
    </ProtectedRoute>
  );
}

