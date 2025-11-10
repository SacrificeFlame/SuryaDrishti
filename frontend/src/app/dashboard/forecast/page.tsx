'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardSidebar from '@/components/dashboard/DashboardSidebar';
import IrradianceForecast from '@/components/dashboard/IrradianceForecast';
import ThemeToggle from '@/components/ThemeToggle';
import { ArrowLeft, RefreshCw, MapPin } from 'lucide-react';
import {
  getLatestSensorReading,
  getMicrogridInfo,
  API_BASE_URL_NO_SUFFIX,
} from '@/lib/api-client';
import { useMicrogridForecast } from '@/hooks/useForecast';
import { ForecastResponse } from '@/types/forecast';
import type { MicrogridForecastResponse } from '@/types/forecast';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

// Helper function to transform MicrogridForecastResponse to ForecastResponse
function transformMicrogridForecastToLegacy(
  microgridForecast: MicrogridForecastResponse | null,
  latestSensorPower: number = 0,
  latestSensorIrradiance: number = 0
): ForecastResponse | null {
  if (!microgridForecast || !microgridForecast.forecast || microgridForecast.forecast.length === 0) {
    return null;
  }

  const forecastPoints = microgridForecast.forecast.slice(0, 10);
  
  const isDaytime = (timestamp: string): boolean => {
    try {
      const date = new Date(timestamp);
      const hour = date.getHours();
      const minute = date.getMinutes();
      const totalMinutes = hour * 60 + minute;
      return totalMinutes >= 399 && totalMinutes < 1140;
    } catch {
      return false;
    }
  };

  const now = new Date();
  
  const forecasts = forecastPoints.map((point) => {
    const pointTime = new Date(point.timestamp);
    const timeLabel = pointTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
    
    let isDay = false;
    
    if (point.timestamp) {
      isDay = isDaytime(point.timestamp);
    }
    
    if (point.solar_elevation !== undefined && point.solar_elevation > 0) {
      isDay = true;
    }
    
    if (point.is_daytime === false) {
      isDay = false;
    } else if (point.is_daytime === true && !isDay) {
      isDay = true;
    }
    
    if (!isDay) {
      return {
        time: timeLabel,
        timestamp: point.timestamp,
        p10: 0,
        p50: 0,
        p90: 0,
        power_output: 0,
      };
    }
    
    return {
      time: timeLabel,
      timestamp: point.timestamp,
      p10: point.ghi.p10,
      p50: point.ghi.p50,
      p90: point.ghi.p90,
      power_output: point.power_kw.mean,
    };
  });

  const firstPoint = microgridForecast.forecast[0];
  const nowDate = new Date();
  const currentHour = nowDate.getHours();
  const currentMinute = nowDate.getMinutes();
  const currentTotalMinutes = currentHour * 60 + currentMinute;
  const isCurrentlyDaytime = currentTotalMinutes >= 399 && currentTotalMinutes < 1140;
  
  const firstPointIsDaytime = firstPoint?.is_daytime !== undefined 
    ? firstPoint.is_daytime 
    : isDaytime(firstPoint?.timestamp || new Date().toISOString());
  
  const currentIrradiance = (!isCurrentlyDaytime || !firstPointIsDaytime) 
    ? 0 
    : (latestSensorIrradiance > 0 
      ? latestSensorIrradiance 
      : (firstPoint?.ghi?.mean || 0));
  const currentPower = (!isCurrentlyDaytime || !firstPointIsDaytime)
    ? 0
    : (latestSensorPower > 0 
      ? latestSensorPower 
      : (firstPoint?.power_kw?.mean || 0));

  return {
    location: {
      lat: microgridForecast.microgrid.location.lat,
      lon: microgridForecast.microgrid.location.lon,
    },
    timestamp: microgridForecast.forecast[0]?.timestamp || new Date().toISOString(),
    forecasts,
    confidence: 1 - (microgridForecast.summary.avg_uncertainty / 1000),
    alerts: [],
    current_irradiance: currentIrradiance,
    current_power_output: currentPower,
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

function ForecastContent() {
  const { user, logout } = useAuth();
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
        const [sensorResult, microgridResult] = await Promise.allSettled([
          getLatestSensorReading(DEFAULT_MICROGRID_ID),
          getMicrogridInfo(DEFAULT_MICROGRID_ID),
        ]);

        const latestSensor = sensorResult.status === 'fulfilled' ? sensorResult.value : null;
        const microgridInfo = microgridResult.status === 'fulfilled' ? microgridResult.value : null;
        
        if (microgridInfo) {
          setLocation({
            lat: microgridInfo.latitude,
            lon: microgridInfo.longitude,
          });
        }
        
        if (microgridForecast) {
          const transformed = transformMicrogridForecastToLegacy(
            microgridForecast,
            latestSensor?.power_output || 0,
            latestSensor?.irradiance || 0
          );
          
          if (transformed) {
            setForecastData(transformed);
          }
        }
      } catch (err) {
        console.error('Error loading forecast data:', err);
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
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-50">Solar Forecast</h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {location.lat.toFixed(4)}°N, {location.lon.toFixed(4)}°E
                  </p>
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
          {loading || forecastLoading ? (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                <p className="mt-4 text-slate-600 dark:text-slate-400">Loading forecast data...</p>
              </div>
            </div>
          ) : forecastError ? (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
              <p className="text-red-800 dark:text-red-300">
                Error loading forecast: {forecastError}
              </p>
            </div>
          ) : forecastData ? (
            <div className="max-w-7xl mx-auto">
              <IrradianceForecast
                forecasts={forecastData.forecasts}
                currentIrradiance={forecastData.current_irradiance}
                currentPower={forecastData.current_power_output}
                confidence={forecastData.confidence}
              />
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-600 dark:text-slate-400">No forecast data available</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function ForecastPage() {
  return (
    <ProtectedRoute>
      <ForecastContent />
    </ProtectedRoute>
  );
}

