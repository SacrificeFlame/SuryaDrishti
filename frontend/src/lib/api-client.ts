// Get API URL from environment variable
// In production (Railway), this MUST be set to your backend's public URL
// Example: https://your-backend.railway.app/api/v1
// 
// IMPORTANT: For Railway deployment, set NEXT_PUBLIC_API_URL environment variable
// in Railway frontend service to your backend's Railway URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Get base URL without /api/v1 suffix (for profile pictures, etc.)
export const API_BASE_URL_NO_SUFFIX = API_BASE_URL.replace('/api/v1', '');

// Log API URL in development to help with debugging
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  console.log('API Base URL:', API_BASE_URL);
  console.log('API Base URL (no suffix):', API_BASE_URL_NO_SUFFIX);
}

// Import types
import type { NotificationPreferences, NotificationPreferenceRequest } from '@/types/notifications';
import type { EnergyLossReport, PerformanceReport } from '@/types/reports';

export interface ForecastScheduleResponse {
  status: string;
  data?: {
    meta: {
      generated_at: string;
      location: { lat: number; lon: number };
      forecast_horizon_hours: number;
      source: string;
    };
    schedule: Array<{
      step: number;
      time: string;
      solar_kW: number;
      load_kW: number;
      charging_kW: number;
      discharging_kW: number;
      soc_percent: number;
    }>;
    soc_target: number;
    forecast_kW: number[];
    weather: Array<{
      time: string;
      ghi: number;
      cloud: number;
      poa_global: number;
      predicted_kW: number;
    }>;
  };
  output?: any;
}

export interface SystemStatusResponse {
  uptime_hours?: number;
  battery: {
    soc: number;
    voltage: number;
    current: number;
  };
  diesel: {
    status: string;
    fuelLevel: number;
  };
  loads: {
    critical: number;
    nonCritical: number;
  };
  timestamp: string;
  recent_actions: Array<{
    action: string;
    timestamp: string;
    details: string;
  }>;
}

export interface AlertResponse {
  id: number;
  microgrid_id: string;
  timestamp: string;
  severity: string;
  message: string;
  action_taken: string | null;
  resolved_at: string | null;
  acknowledged: boolean;
}

export interface SensorReadingResponse {
  id: number;
  microgrid_id: string;
  timestamp: string;
  irradiance: number;
  power_output: number;
  temperature: number;
  humidity: number;
  wind_speed?: number;
  wind_direction?: number;
}

export interface MicrogridInfo {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  capacity_kw: number;
  created_at: string;
}

// Fetch forecast and schedule data
export async function getForecastSchedule(forecastHours: number = 12): Promise<ForecastScheduleResponse> {
  const response = await fetch(`${API_BASE_URL}/forecast/schedule?forecast_hours=${forecastHours}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch forecast: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

// Fetch NGBoost forecast (alternative)
export async function getNGBoostForecast(
  lat: number,
  lon: number,
  horizonHours: number = 24
): Promise<any> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    horizon_hours: horizonHours.toString(),
  });
  
  const response = await fetch(`${API_BASE_URL}/forecast/ngboost?${params}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch NGBoost forecast: ${response.status}`);
  }
  
  return response.json();
}

// Get system status
export async function getSystemStatus(microgridId: string): Promise<SystemStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/status`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch system status: ${response.status}`);
  }
  
  return response.json();
}

// Get alerts
export async function getAlerts(microgridId: string, limit: number = 20): Promise<AlertResponse[]> {
  const response = await fetch(`${API_BASE_URL}/alerts/${microgridId}?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch alerts: ${response.status}`);
  }
  
  return response.json();
}

// Get latest sensor reading
export async function getLatestSensorReading(microgridId: string): Promise<SensorReadingResponse> {
  const response = await fetch(`${API_BASE_URL}/sensors/${microgridId}/latest`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch sensor reading: ${response.status}`);
  }
  
  return response.json();
}

// Get sensor history
export async function getSensorHistory(microgridId: string, limit: number = 100): Promise<SensorReadingResponse[]> {
  const response = await fetch(`${API_BASE_URL}/sensors/${microgridId}/history?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch sensor history: ${response.status}`);
  }
  
  return response.json();
}

// Get microgrid info
export async function getMicrogridInfo(microgridId: string): Promise<MicrogridInfo> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch microgrid info: ${response.status}`);
  }
  
  return response.json();
}

// Device Management APIs
export interface Device {
  id: number;
  microgrid_id: string;
  name: string;
  power_consumption_watts: number;
  device_type: 'essential' | 'flexible' | 'optional';
  minimum_runtime_minutes: number;
  preferred_hours?: { start: number; end: number };
  priority_level: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DeviceCreate {
  name: string;
  power_consumption_watts: number;
  device_type: 'essential' | 'flexible' | 'optional';
  minimum_runtime_minutes?: number;
  preferred_hours?: { start: number; end: number };
  priority_level?: number;
}

export interface DeviceUpdate {
  name?: string;
  power_consumption_watts?: number;
  device_type?: 'essential' | 'flexible' | 'optional';
  minimum_runtime_minutes?: number;
  preferred_hours?: { start: number; end: number };
  priority_level?: number;
  is_active?: boolean;
}

export async function getDevices(microgridId: string, activeOnly: boolean = false): Promise<Device[]> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/devices?active_only=${activeOnly}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch devices: ${response.status}`);
  }
  return response.json();
}

export async function getDevice(microgridId: string, deviceId: number): Promise<Device> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/devices/${deviceId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch device: ${response.status}`);
  }
  return response.json();
}

export async function createDevice(microgridId: string, device: DeviceCreate): Promise<Device> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/devices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(device),
  });
  if (!response.ok) {
    throw new Error(`Failed to create device: ${response.status}`);
  }
  return response.json();
}

export async function updateDevice(microgridId: string, deviceId: number, device: DeviceUpdate): Promise<Device> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/devices/${deviceId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(device),
  });
  if (!response.ok) {
    throw new Error(`Failed to update device: ${response.status}`);
  }
  return response.json();
}

export async function deleteDevice(microgridId: string, deviceId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/devices/${deviceId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete device: ${response.status}`);
  }
}

// Schedule APIs
export interface ScheduleTimeSlot {
  time: string;
  solar_generation_kw: number;
  total_load_kw: number;
  battery_charge_kw: number;
  battery_discharge_kw?: number;
  battery_soc: number;
  grid_import_kw: number;
  grid_export_kw: number;
  generator_power_kw: number;
  devices: Array<{ 
    id: number; 
    name: string; 
    power_kw: number;
    power_source?: string; // 'solar', 'battery', 'grid', 'generator', 'solar+battery', etc.
    is_irrigation_pump?: boolean;
  }>;
}

export interface Schedule {
  id: number;
  microgrid_id: string;
  date: string;
  schedule_data: {
    schedule: ScheduleTimeSlot[];
    metrics: OptimizationMetrics;
    initial_battery_soc: number;
    final_battery_soc: number;
  };
  optimization_metrics?: OptimizationMetrics;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OptimizationMetrics {
  solar_utilization_percent: number;
  grid_import_reduction_percent: number;
  estimated_cost_savings: number;
  battery_cycle_efficiency: number;
  carbon_footprint_reduction_kg: number;
  generator_runtime_minutes: number;
  total_energy_kwh: number;
  solar_energy_kwh: number;
  grid_energy_kwh: number;
  grid_export_energy_kwh: number;
  grid_export_revenue: number;
  battery_energy_kwh: number;
  generator_energy_kwh: number;
}

export interface ScheduleGenerateRequest {
  date?: string;
  use_forecast?: boolean;
  optimization_mode?: 'cost' | 'battery_longevity' | 'grid_independence';
}

export async function generateSchedule(microgridId: string, request: ScheduleGenerateRequest = {}): Promise<Schedule> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/schedules/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Failed to generate schedule: ${response.status}`);
  }
  return response.json();
}

export async function getSchedules(microgridId: string, date?: string, limit: number = 10): Promise<Schedule[]> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (date) params.append('date', date);
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/schedules?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch schedules: ${response.status}`);
  }
  return response.json();
}

export async function getSchedule(microgridId: string, scheduleId: number): Promise<Schedule> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/schedules/${scheduleId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch schedule: ${response.status}`);
  }
  return response.json();
}

// Configuration APIs
export interface SystemConfiguration {
  id: number;
  microgrid_id: string;
  battery_capacity_kwh: number;
  battery_max_charge_rate_kw: number;
  battery_max_discharge_rate_kw: number;
  battery_efficiency: number;
  battery_min_soc: number;
  battery_max_soc: number;
  grid_peak_rate_per_kwh: number;
  grid_off_peak_rate_per_kwh: number;
  grid_peak_hours?: { start: number; end: number };
  grid_export_rate_per_kwh: number;
  grid_export_enabled: boolean;
  generator_fuel_consumption_l_per_kwh: number;
  generator_fuel_cost_per_liter: number;
  generator_min_runtime_minutes: number;
  generator_max_power_kw: number;
  optimization_mode: 'cost' | 'battery_longevity' | 'grid_independence';
  safety_margin_critical_loads: number;
  created_at: string;
  updated_at: string;
}

export interface SystemConfigurationUpdate {
  battery_capacity_kwh?: number;
  battery_max_charge_rate_kw?: number;
  battery_max_discharge_rate_kw?: number;
  battery_efficiency?: number;
  battery_min_soc?: number;
  battery_max_soc?: number;
  grid_peak_rate_per_kwh?: number;
  grid_off_peak_rate_per_kwh?: number;
  grid_peak_hours?: { start: number; end: number };
  grid_export_rate_per_kwh?: number;
  grid_export_enabled?: boolean;
  generator_fuel_consumption_l_per_kwh?: number;
  generator_fuel_cost_per_liter?: number;
  generator_min_runtime_minutes?: number;
  generator_max_power_kw?: number;
  optimization_mode?: 'cost' | 'battery_longevity' | 'grid_independence';
  safety_margin_critical_loads?: number;
}

export async function getConfiguration(microgridId: string): Promise<SystemConfiguration> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/configuration`);
  if (!response.ok) {
    throw new Error(`Failed to fetch configuration: ${response.status}`);
  }
  return response.json();
}

export async function updateConfiguration(microgridId: string, config: SystemConfigurationUpdate): Promise<SystemConfiguration> {
  const response = await fetch(`${API_BASE_URL}/microgrid/${microgridId}/configuration`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    throw new Error(`Failed to update configuration: ${response.status}`);
  }
  return response.json();
}

// Notification APIs
export async function getNotificationPreferences(microgridId: string): Promise<NotificationPreferences> {
  const response = await fetch(`${API_BASE_URL}/notifications/preferences/${microgridId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch notification preferences: ${response.status}`);
  }
  return response.json();
}

export async function updateNotificationPreferences(
  microgridId: string,
  preferences: NotificationPreferenceRequest
): Promise<NotificationPreferences> {
  const response = await fetch(`${API_BASE_URL}/notifications/preferences/${microgridId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences),
  });
  if (!response.ok) {
    throw new Error(`Failed to update notification preferences: ${response.status}`);
  }
  return response.json();
}

export async function sendTestNotification(microgridId: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/notifications/send-test/${microgridId}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to send test notification: ${response.status}`);
  }
  return response.json();
}

// Alert APIs
export async function acknowledgeAlert(alertId: number, acknowledged: boolean = true): Promise<{ status: string; alert_id: number; acknowledged: boolean }> {
  const response = await fetch(`${API_BASE_URL}/alerts/${alertId}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ acknowledged }),
  });
  if (!response.ok) {
    throw new Error(`Failed to acknowledge alert: ${response.status}`);
  }
  return response.json();
}

// Report APIs
export async function getEnergyLossReport(
  microgridId: string,
  startDate: string,
  endDate: string
): Promise<EnergyLossReport> {
  const response = await fetch(
    `${API_BASE_URL}/reports/energy-loss/${microgridId}?start_date=${startDate}&end_date=${endDate}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch energy loss report: ${response.status}`);
  }
  return response.json();
}

export async function getPerformanceReport(
  microgridId: string,
  days: number = 7
): Promise<PerformanceReport> {
  const response = await fetch(`${API_BASE_URL}/reports/performance/${microgridId}?days=${days}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch performance report: ${response.status}`);
  }
  return response.json();
}

