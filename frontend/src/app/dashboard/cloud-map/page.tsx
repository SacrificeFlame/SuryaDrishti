'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardSidebar from '@/components/dashboard/DashboardSidebar';
import CloudMovementMap from '@/components/dashboard/CloudMovementMap';
import ThemeToggle from '@/components/ThemeToggle';
import { ArrowLeft, RefreshCw, Map } from 'lucide-react';
import { getMicrogridInfo } from '@/lib/api-client';
import { useMicrogridForecast } from '@/hooks/useForecast';
import { ForecastResponse } from '@/types/forecast';
import type { MicrogridForecastResponse } from '@/types/forecast';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

// Helper function to transform forecast data
function transformMicrogridForecastToLegacy(
  microgridForecast: MicrogridForecastResponse | null,
): ForecastResponse | null {
  if (!microgridForecast) {
    return null;
  }

  return {
    location: {
      lat: microgridForecast.microgrid.location.lat,
      lon: microgridForecast.microgrid.location.lon,
    },
    timestamp: microgridForecast.forecast[0]?.timestamp || new Date().toISOString(),
    forecasts: [],
    confidence: 1 - (microgridForecast.summary.avg_uncertainty / 1000),
    alerts: [],
    current_irradiance: 0,
    current_power_output: 0,
    cloud_data: {
      cloud_map: Array(20).fill(null).map(() => 
        Array(20).fill(null).map(() => Math.random() > 0.7 ? Math.random() : 0)
      ),
      motion_vectors: Array(20).fill(null).map(() => 
        Array(20).fill(null).map(() => ({
          x: (Math.random() - 0.5) * 2,
          y: (Math.random() - 0.5) * 2
        }))
      ),
    },
  };
}

function CloudMapContent() {
  const { user } = useAuth();
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [location, setLocation] = useState({ lat: 28.4595, lon: 77.0266 });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const { 
    forecast: microgridForecast, 
    loading: forecastLoading, 
    error: forecastError,
    refetch
  } = useMicrogridForecast(DEFAULT_MICROGRID_ID, {
    horizonHours: 24,
    trainingDays: 180,
    autoRefresh: true,
    refreshInterval: 15 * 60 * 1000,
  });

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const microgridInfo = await getMicrogridInfo(DEFAULT_MICROGRID_ID);
        setLocation({ lat: microgridInfo.latitude, lon: microgridInfo.longitude });
        
        if (microgridForecast) {
          const transformed = transformMicrogridForecastToLegacy(microgridForecast);
          if (transformed) {
            setForecastData(transformed);
          }
        }
      } catch (err) {
        console.error('Error loading cloud map data:', err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [microgridForecast]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setTimeout(() => setRefreshing(false), 1000);
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
                  <div className="w-10 h-10 rounded-lg bg-sky-100 dark:bg-sky-900/20 flex items-center justify-center">
                    <Map className="w-5 h-5 text-sky-600 dark:text-sky-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">Cloud Movement Map</h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {location.lat.toFixed(4)}°N, {location.lon.toFixed(4)}°E
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleRefresh}
                  disabled={refreshing || forecastLoading}
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
            {(() => {
              if (loading || forecastLoading) {
                return (
                  <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                      <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                      <p className="mt-4 text-slate-600 dark:text-slate-400">Loading cloud map data...</p>
                    </div>
                  </div>
                );
              }
              
              if (forecastError) {
                return (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
                    <p className="text-red-800 dark:text-red-300">
                      Error loading cloud map: {forecastError}
                    </p>
                  </div>
                );
              }
              
              const cloudData = forecastData?.cloud_data;
              if (cloudData && forecastData) {
                return (
                  <CloudMovementMap
                    cloudData={cloudData}
                    location={forecastData.location}
                  />
                );
              }
              
              return (
                <div className="text-center py-12">
                  <p className="text-slate-600 dark:text-slate-400">No cloud map data available</p>
                </div>
              );
            })()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function CloudMapPage() {
  return (
    <ProtectedRoute>
      <CloudMapContent />
    </ProtectedRoute>
  );
}

