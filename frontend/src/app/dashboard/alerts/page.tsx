'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import HamburgerMenu from '@/components/dashboard/HamburgerMenu';
import AlertsPanel from '@/components/dashboard/AlertsPanel';
import ThemeToggle from '@/components/ThemeToggle';
import { ArrowLeft, RefreshCw, Filter } from 'lucide-react';
import { getAlerts, acknowledgeAlert } from '@/lib/api-client';
import { Alert } from '@/types/forecast';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function AlertsContent() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'info'>('all');

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 30 * 1000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadAlerts = async () => {
    try {
      const alertsData = await getAlerts(DEFAULT_MICROGRID_ID, 50);
      setAlerts(
        alertsData.map((alert) => ({
          id: alert.id,
          severity: alert.severity as 'info' | 'warning' | 'critical' | 'success',
          message: alert.message,
          timestamp: alert.timestamp,
          action: alert.action_taken,
          acknowledged: alert.acknowledged,
        }))
      );
    } catch (err) {
      console.error('Error loading alerts:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAlerts();
  };

  const handleAcknowledge = async (alertId: number) => {
    try {
      await acknowledgeAlert(alertId, true);
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, acknowledged: true } : a));
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(a => a.severity === filter);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex">
      <HamburgerMenu />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Header */}
        <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 sm:gap-4">
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-50">Alerts</h1>
                  <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                    {alerts.length} total alerts
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 sm:gap-4">
                <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
                  {(['all', 'critical', 'warning', 'info'] as const).map((f) => (
                    <button
                      key={f}
                      onClick={() => setFilter(f)}
                      className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                        filter === f
                          ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-50 shadow-sm'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-50'
                      }`}
                    >
                      {f.charAt(0).toUpperCase() + f.slice(1)}
                    </button>
                  ))}
                </div>
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
                  <p className="mt-4 text-slate-600 dark:text-slate-400">Loading alerts...</p>
                </div>
              </div>
            ) : (
              <AlertsPanel 
                alerts={filteredAlerts} 
                onAlertAcknowledged={handleAcknowledge}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function AlertsPage() {
  return (
    <ProtectedRoute>
      <AlertsContent />
    </ProtectedRoute>
  );
}

