'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import ThemeToggle from '@/components/ThemeToggle';
import ForecastSchedule from '@/components/dashboard/ForecastSchedule';
import { useMicrogridForecast } from '@/hooks/useForecast';
import { generateSchedule } from '@/lib/api-client';
import { getMicrogridInfo } from '@/lib/api-client';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

interface ForecastScheduleResponse {
  status: string;
  stdout?: string;
  stderr?: string;
  data?: {
    meta: {
      generated_at: string;
      location: { lat: number; lon: number };
      forecast_horizon_hours: number;
      source?: string;
      sources?: string[];
    };
    weather?: Array<{
      time: string;
      ghi: number;
      cloud: number;
      poa_global: number;
      predicted_kW: number;
    }>;
    forecast_kW?: number[];
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
  output?: {
    meta: {
      generated_at: string;
      location: { lat: number; lon: number };
      forecast_horizon_hours: number;
      sources?: string[];
    };
    schedule: Array<{
      time: string;
      source?: string;
      'Solar (kW)'?: number;
      'Load (kW)'?: number;
      'Charging (kW)'?: number;
      'Discharging (kW)'?: number;
      'SOC (%)'?: number;
      solar_kW?: number;
      load_kW?: number;
      charging_kW?: number;
      discharging_kW?: number;
      soc_percent?: number;
    }>;
    soc_target: number;
  };
}

function ForecastScheduleContent() {
  const { user, isTrialActive, trialDaysRemaining, logout } = useAuth();
  const [scheduleData, setScheduleData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forecastHours, setForecastHours] = useState(24);
  const [currentTime, setCurrentTime] = useState<string>('');
  const [location, setLocation] = useState({ lat: 28.4595, lon: 77.0266 });

  // Use the SAME forecast hook as the dashboard - no duplicate API calls!
  const { 
    forecast: microgridForecast, 
    loading: forecastLoading, 
    error: forecastError 
  } = useMicrogridForecast(DEFAULT_MICROGRID_ID, {
    horizonHours: forecastHours,
    trainingDays: 180,
    autoRefresh: true,
    refreshInterval: 15 * 60 * 1000, // 15 minutes
  });

  // Fetch location and generate schedule when forecast is available
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        // Get location
        const microgridInfo = await getMicrogridInfo(DEFAULT_MICROGRID_ID);
        setLocation({ lat: microgridInfo.latitude, lon: microgridInfo.longitude });

        // Wait for forecast to be available
        if (!microgridForecast) {
          return;
        }

        // Generate schedule using the existing forecast
        const schedule = await generateSchedule(DEFAULT_MICROGRID_ID, {
          date: new Date().toISOString().split('T')[0],
          use_forecast: true, // Use the forecast we already have
          optimization_mode: 'cost',
        });

        // Transform schedule data to match ForecastSchedule component format
        const scheduleSlots = schedule.schedule_data?.schedule || [];
        const transformedSchedule = scheduleSlots.map((slot: any, idx: number) => ({
          step: idx + 1,
          time: slot.time,
          solar_kW: slot.solar_generation_kw || 0,
          load_kW: slot.total_load_kw || 0,
          charging_kW: slot.battery_charge_kw || 0,
          discharging_kW: slot.battery_discharge_kw || 0,
          soc_percent: (slot.battery_soc || 0) * 100,
        }));

        // Extract forecast values from schedule
        const forecast_kW = transformedSchedule.map((s: any) => s.solar_kW);
        
        // Create weather array from forecast
        const weather = transformedSchedule.map((s: any) => ({
          time: s.time,
          ghi: s.solar_kW * 20, // Approximate GHI from power
          cloud: 0,
          poa_global: s.solar_kW * 20,
          predicted_kW: s.solar_kW,
        }));

        setScheduleData({
          meta: {
            generated_at: schedule.created_at || new Date().toISOString(),
            location: { lat: microgridInfo.latitude, lon: microgridInfo.longitude },
            forecast_horizon_hours: forecastHours,
            source: 'internal_ngboost_openmeteo',
          },
          schedule: transformedSchedule,
          soc_target: 0.8,
          forecast_kW: forecast_kW,
          weather: weather,
        });
      } catch (err) {
        console.error('[Schedule] Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to generate schedule');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [microgridForecast, forecastHours]);

  useEffect(() => {
    setCurrentTime(new Date().toLocaleTimeString());
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    // The forecast will auto-refresh via the hook, which will trigger schedule regeneration
    setLoading(true);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-300">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-300 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 group">
              <span className="text-2xl group-hover:rotate-12 transition-transform duration-300">☀️</span>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white group-hover:text-yellow-600 dark:group-hover:text-yellow-400 transition-colors">
                  SuryaDrishti
                </h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">Solar Forecasting Dashboard</p>
              </div>
            </Link>
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors"
              >
                Dashboard
              </Link>
              <Link
                href="/"
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors hidden sm:block"
              >
                Home
              </Link>
              {isTrialActive && (
                <div className="hidden md:flex items-center gap-2 bg-yellow-100 dark:bg-yellow-900/30 px-3 py-1 rounded-full">
                  <span className="text-xs font-semibold text-yellow-800 dark:text-yellow-300">
                    Trial: {trialDaysRemaining} days left
                  </span>
                </div>
              )}
              <div className="text-right hidden md:block">
                <div className="text-sm text-gray-600 dark:text-gray-400">{user?.username || 'User'}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {location.lat.toFixed(4)}°N, {location.lon.toFixed(4)}°E
                </div>
              </div>
              <ThemeToggle />
              <button
                onClick={logout}
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                title="Logout"
              >
                Logout
              </button>
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse shadow-lg shadow-green-500/50"></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors duration-300">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Battery Schedule</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Optimized schedule using forecast from dashboard
              </p>
            </div>
            <div className="flex items-center gap-4">
              <label className="text-sm text-gray-600 dark:text-gray-400">
                Forecast Hours:
                <select
                  value={forecastHours}
                  onChange={(e) => setForecastHours(Number(e.target.value))}
                  className="ml-2 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value={6}>6 hours</option>
                  <option value={12}>12 hours</option>
                  <option value={24}>24 hours</option>
                  <option value={48}>48 hours</option>
                </select>
              </label>
              <button
                onClick={handleRefresh}
                disabled={loading || forecastLoading}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {(loading || forecastLoading) ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {(error || forecastError) && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-300">
              Error: {error || forecastError || 'Failed to load schedule'}
            </p>
          </div>
        )}

        {/* Schedule Component - No forecast display, just schedule */}
        {scheduleData && (
          <ForecastSchedule
            data={scheduleData}
            location={location}
            loading={loading || forecastLoading}
          />
        )}

        {(loading || forecastLoading) && !scheduleData && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading schedule...</p>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
              Using forecast from dashboard to generate optimized schedule
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
            <div>
              Last updated: {currentTime || 'Loading...'}
            </div>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                API Connected
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function ForecastSchedulePage() {
  return (
    <ProtectedRoute>
      <ForecastScheduleContent />
    </ProtectedRoute>
  );
}

