'use client';

import CloudMovementMap from '@/components/dashboard/CloudMovementMap';
import IrradianceForecast from '@/components/dashboard/IrradianceForecast';
import AlertsPanel from '@/components/dashboard/AlertsPanel';
import SystemStatus from '@/components/dashboard/SystemStatus';
import PerformanceMetrics from '@/components/dashboard/PerformanceMetrics';
import ActionsLog from '@/components/dashboard/ActionsLog';
import {
  mockForecastData,
  mockSystemStatus,
  mockRecentAlerts,
  mockPerformanceMetrics,
  mockActionsLog
} from '@/lib/mockData';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">☀️ SuryaDrishti</h1>
              <p className="text-sm text-gray-600">Solar Forecasting for Rural Microgrids</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-gray-600">Rajasthan Solar Grid 1</div>
                <div className="text-xs text-gray-500">
                  {mockForecastData.location.lat.toFixed(4)}°N, {mockForecastData.location.lon.toFixed(4)}°E
                </div>
              </div>
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
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
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div>
              Last updated: {new Date().toLocaleTimeString()}
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
