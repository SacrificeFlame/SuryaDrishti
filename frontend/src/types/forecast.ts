export interface ForecastPoint {
  time: string;
  timestamp: string;
  p10: number;
  p50: number;
  p90: number;
  power_output: number;
}

export interface CloudData {
  cloud_map: number[][];
  motion_vectors: Array<Array<{ x: number; y: number }>>;
  predicted_paths?: Array<Array<{ lat: number; lon: number; timestamp: string }>>;
}

export interface Alert {
  id?: number;
  severity: 'info' | 'warning' | 'critical' | 'success';
  message: string;
  timestamp: string;
  action?: string | null;
}

export interface ForecastResponse {
  location: { lat: number; lon: number };
  timestamp: string;
  forecasts: ForecastPoint[];
  confidence: number;
  alerts: Alert[];
  cloud_data?: CloudData;
  current_irradiance: number;
  current_power_output: number;
}

export interface Microgrid {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  capacity_kw: number;
  created_at: string;
}

export interface SystemStatus {
  battery_soc: number;
  diesel_status: 'standby' | 'running' | 'off';
  load_kw: number;
  solar_generation_kw: number;
  grid_import_kw: number;
  uptime_hours: number;
  last_updated: string;
}

export interface SensorReading {
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

