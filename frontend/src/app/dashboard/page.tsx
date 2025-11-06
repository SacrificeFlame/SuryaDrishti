'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import CloudMovementMap from '@/components/dashboard/CloudMovementMap';
import IrradianceForecast from '@/components/dashboard/IrradianceForecast';
import AlertsPanel from '@/components/dashboard/AlertsPanel';
import SystemStatus from '@/components/dashboard/SystemStatus';
import PerformanceMetrics from '@/components/dashboard/PerformanceMetrics';
import ActionsLog from '@/components/dashboard/ActionsLog';
import ThemeToggle from '@/components/ThemeToggle';
import {
  mockForecastData,
  mockSystemStatus,
  mockRecentAlerts,
  mockPerformanceMetrics,
  mockActionsLog
} from '@/lib/mockData';

function DashboardContent() {
  const [currentTime, setCurrentTime] = useState<string>('');
  const { user, isTrialActive, trialDaysRemaining, logout } = useAuth();

  useEffect(() => {
    // Set time only on client side to avoid hydration mismatch
    setCurrentTime(new Date().toLocaleTimeString());
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

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
                href="/"
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors hidden sm:block"
              >
                Home
              </Link>
              <Link
                href="/purchase"
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors hidden sm:block"
              >
                Upgrade
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
                <div className="text-xs text-gray-500 dark:text-gray-500">
                  {mockForecastData.location.lat.toFixed(4)}°N, {mockForecastData.location.lon.toFixed(4)}°E
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
        {/* Performance Metrics */}
        <div className="mb-8">
          <PerformanceMetrics metrics={mockPerformanceMetrics} />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Left Column - Forecast and Cloud Map */}
          <div className="lg:col-span-2 space-y-8">
            <IrradianceForecast
              forecasts={mockForecastData.forecasts}
              currentIrradiance={mockForecastData.current_irradiance}
              currentPower={mockForecastData.current_power_output}
              confidence={mockForecastData.confidence}
            />
            
            <CloudMovementMap
              cloudData={mockForecastData.cloud_data!}
              location={mockForecastData.location}
            />
          </div>

          {/* Right Column - Alerts and Status */}
          <div className="space-y-8">
            <AlertsPanel alerts={mockRecentAlerts} />
            <SystemStatus status={mockSystemStatus} />
          </div>
        </div>

        {/* Actions Log */}
        <div>
          <ActionsLog actions={mockActionsLog} />
        </div>
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
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                ML Models Active
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
