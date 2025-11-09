import { ForecastResponse, SystemStatus, Alert } from '@/types/forecast';

// Mock forecast data
export const mockForecastData: ForecastResponse = {
  location: {
    lat: 28.4595,
    lon: 77.0266
  },
  timestamp: new Date().toISOString(),
  current_irradiance: 850,
  current_power_output: 40.5,
  confidence: 0.87,
  forecasts: [
    { time: '5m', timestamp: new Date(Date.now() + 5 * 60000).toISOString(), p10: 820, p50: 850, p90: 880, power_output: 40.2 },
    { time: '10m', timestamp: new Date(Date.now() + 10 * 60000).toISOString(), p10: 800, p50: 830, p90: 860, power_output: 39.5 },
    { time: '15m', timestamp: new Date(Date.now() + 15 * 60000).toISOString(), p10: 780, p50: 810, p90: 840, power_output: 38.5 },
    { time: '30m', timestamp: new Date(Date.now() + 30 * 60000).toISOString(), p10: 750, p50: 780, p90: 810, power_output: 37.0 },
    { time: '45m', timestamp: new Date(Date.now() + 45 * 60000).toISOString(), p10: 720, p50: 750, p90: 780, power_output: 35.6 },
    { time: '60m', timestamp: new Date(Date.now() + 60 * 60000).toISOString(), p10: 700, p50: 730, p90: 760, power_output: 34.7 },
    { time: '75m', timestamp: new Date(Date.now() + 75 * 60000).toISOString(), p10: 680, p50: 710, p90: 740, power_output: 33.7 },
    { time: '90m', timestamp: new Date(Date.now() + 90 * 60000).toISOString(), p10: 660, p50: 690, p90: 720, power_output: 32.8 },
    { time: '105m', timestamp: new Date(Date.now() + 105 * 60000).toISOString(), p10: 640, p50: 670, p90: 700, power_output: 31.8 },
    { time: '120m', timestamp: new Date(Date.now() + 120 * 60000).toISOString(), p10: 620, p50: 650, p90: 680, power_output: 30.9 }
  ],
  alerts: [],
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
  }
};

// Mock system status
export const mockSystemStatus: SystemStatus = {
  battery_soc: 72,
  diesel_status: 'off',
  load_kw: 38.5,
  solar_generation_kw: 40.5,
  grid_import_kw: 0,
  uptime_hours: 1247,
  last_updated: new Date().toISOString()
};

// Mock recent alerts
export const mockRecentAlerts: Alert[] = [
  {
    id: 1,
    severity: 'warning',
    message: 'Cloud cover approaching - Expected 15% power reduction in 30 minutes',
    timestamp: new Date(Date.now() - 10 * 60000).toISOString(),
    action: 'Consider activating battery backup mode'
  },
  {
    id: 2,
    severity: 'info',
    message: 'Forecast confidence above 85% - High reliability',
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
    action: null
  },
  {
    id: 3,
    severity: 'success',
    message: 'Battery charging complete - SOC at 72%',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    action: null
  }
];

// Mock performance metrics
export const mockPerformanceMetrics = {
  dieselSavings: 45.2,
  forecastAccuracy: 87.5,
  uptime: 99.2,
  co2Avoided: 125.8
};

// Mock actions log
export const mockActionsLog = [
  {
    id: 1,
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
    action: 'Forecast generated',
    reason: '60-minute forecast for microgrid_001',
    status: 'completed'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    action: 'Battery mode changed',
    reason: 'Switched to charging mode (SOC: 68% → 72%)',
    status: 'completed'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
    action: 'Cloud detection',
    reason: 'Detected cloud movement: 2.3 m/s NW direction',
    status: 'completed'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    action: 'Alert generated',
    reason: 'Cloud cover warning for microgrid_001',
    status: 'completed'
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
    action: 'Forecast generated',
    reason: '60-minute forecast for microgrid_001',
    status: 'completed'
  }
];

