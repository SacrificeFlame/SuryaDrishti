'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import HamburgerMenu from '@/components/dashboard/HamburgerMenu';
import AccountPanel from '@/components/dashboard/AccountPanel';
import ThemeToggle from '@/components/ThemeToggle';
import ForecastSchedule from '@/components/dashboard/ForecastSchedule';
import { useMicrogridForecast } from '@/hooks/useForecast';
import { generateSchedule } from '@/lib/api-client';
import { getMicrogridInfo } from '@/lib/api-client';
import { ArrowLeft, RefreshCw } from 'lucide-react';

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

function BatterySchedulerContent() {
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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex">
      <HamburgerMenu />
      
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Header */}
        <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 sm:gap-4">
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-50">Battery Scheduler</h1>
                  <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                    Optimized battery charging and discharging schedule
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 sm:gap-4">
                <button
                  onClick={handleRefresh}
                  disabled={loading || forecastLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${loading || forecastLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
                <AccountPanel />
                <ThemeToggle />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            {/* Controls */}
            <div className="mb-6 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg p-6">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50">Schedule Configuration</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    Optimized schedule using forecast data
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <label className="text-sm text-slate-600 dark:text-slate-400">
                    Forecast Hours:
                    <select
                      value={forecastHours}
                      onChange={(e) => setForecastHours(Number(e.target.value))}
                      className="ml-2 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50 focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    >
                      <option value={6}>6 hours</option>
                      <option value={12}>12 hours</option>
                      <option value={24}>24 hours</option>
                      <option value={48}>48 hours</option>
                    </select>
                  </label>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {(error || forecastError) && (
              <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-sm font-semibold text-red-800 dark:text-red-300 mb-2">
                  Error: Failed to connect to backend server
                </p>
                <p className="text-xs text-red-700 dark:text-red-400">
                  {error?.includes('CORS') || forecastError?.includes('CORS') 
                    ? 'CORS error: Backend server may not be configured to allow requests from this domain.'
                    : error || forecastError || 'Please check if the backend server is running and accessible.'}
                </p>
                <p className="text-xs text-red-600 dark:text-red-500 mt-2">
                  If this persists, check your network connection and backend service status.
                </p>
              </div>
            )}

            {/* Schedule Component */}
            {scheduleData && (
              <ForecastSchedule
                data={scheduleData}
                location={location}
                loading={loading || forecastLoading}
              />
            )}

            {(loading || forecastLoading) && !scheduleData && (
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-lg p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                <p className="mt-4 text-slate-600 dark:text-slate-400">Loading schedule...</p>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-500">
                  Generating optimized battery schedule from forecast data
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function BatterySchedulerPage() {
  return (
    <ProtectedRoute>
      <BatterySchedulerContent />
    </ProtectedRoute>
  );
}

