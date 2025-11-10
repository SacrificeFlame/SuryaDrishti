'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardSidebar from '@/components/dashboard/DashboardSidebar';
import SystemStatus from '@/components/dashboard/SystemStatus';
import ThemeToggle from '@/components/ThemeToggle';
import { ArrowLeft, RefreshCw, Activity } from 'lucide-react';
import { getSystemStatus, getLatestSensorReading } from '@/lib/api-client';
import { SystemStatus as SystemStatusType } from '@/types/forecast';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function SystemStatusContent() {
  const { user } = useAuth();
  const [systemStatus, setSystemStatus] = useState<SystemStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 2 * 60 * 1000); // Refresh every 2 minutes
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const [statusResponse, latestSensor] = await Promise.allSettled([
        getSystemStatus(DEFAULT_MICROGRID_ID),
        getLatestSensorReading(DEFAULT_MICROGRID_ID),
      ]);

      if (statusResponse.status === 'fulfilled') {
        const status = statusResponse.value;
        const solarGen = latestSensor.status === 'fulfilled' ? latestSensor.value.power_output : 0;
        const totalLoad = status.loads.critical + status.loads.nonCritical;
        
        setSystemStatus({
          battery_soc: status.battery.soc,
          diesel_status: status.diesel.status as 'standby' | 'running' | 'off',
          load_kw: totalLoad,
          solar_generation_kw: solarGen,
          grid_import_kw: Math.max(0, totalLoad - solarGen - (status.battery.current > 0 ? status.battery.current * 0.05 : 0)),
          uptime_hours: status.uptime_hours || 0,
          last_updated: status.timestamp,
        });
      }
    } catch (err) {
      console.error('Error loading system status:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadStatus();
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
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center">
                    <Activity className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">System Status</h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      Real-time system monitoring
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
          <div className="max-w-7xl mx-auto">
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                  <p className="mt-4 text-slate-600 dark:text-slate-400">Loading system status...</p>
                </div>
              </div>
            ) : systemStatus ? (
              <SystemStatus status={systemStatus} />
            ) : (
              <div className="text-center py-12">
                <p className="text-slate-600 dark:text-slate-400">No system status data available</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function SystemStatusPage() {
  return (
    <ProtectedRoute>
      <SystemStatusContent />
    </ProtectedRoute>
  );
}

