/**
 * Forecast API Type Definitions
 * Types for all forecast API endpoints
 */

// NGBoost Forecast Types
export interface NGBoostForecastPoint {
  time: string;
  timestamp: string;
  p10: number;
  p50: number;
  p90: number;
  mean: number;
  std: number;
  ghi: number;
  ghi_clear_sky?: number;
  clear_sky_ratio?: number | null;
  clear_sky_index?: number;
  solar_elevation?: number;
  is_daytime?: boolean;
}

export interface NGBoostForecastResponse {
  status: string;
  model: string;
  location: {
    lat: number;
    lon: number;
  };
  horizon_hours: number;
  forecast: NGBoostForecastPoint[];
  summary: {
    mean_ghi: number;
    max_ghi: number;
    min_ghi: number;
    avg_uncertainty: number;
  };
  metadata: {
    data_source: string;
    retrained: boolean;
    training_days: number;
    n_samples: number;
    features_used: number;
  };
}

// Microgrid Forecast Types
export interface MicrogridForecastPoint {
  time: string;
  timestamp: string;
  ghi: {
    p10: number;
    p50: number;
    p90: number;
    mean: number;
    std: number;
    clear_sky?: number;
    clear_sky_ratio?: number;
  };
  power_kw: {
    p10: number;
    p50: number;
    p90: number;
    mean: number;
    clear_sky?: number;
  };
  energy_kwh: number;
  solar_elevation?: number;
  is_daytime?: boolean;
}

export interface MicrogridForecastResponse {
  status: string;
  model: string;
  microgrid: {
    id: string;
    name: string;
    location: {
      lat: number;
      lon: number;
    };
    capacity_kw: number;
  };
  horizon_hours: number;
  forecast: MicrogridForecastPoint[];
  summary: {
    ghi: {
      mean: number;
      max: number;
      min: number;
    };
    power_kw: {
      mean: number;
      max: number;
      min: number;
    };
    total_energy_kwh: number;
    avg_uncertainty: number;
  };
  metadata: {
    data_source: string;
    retrained: boolean;
    training_days: number;
    n_samples: number;
    features_used: number;
  };
}

// Hybrid Forecast Types (extends NGBoost)
export interface HybridForecastResponse extends NGBoostForecastResponse {
  satellite: {
    satellite_available: boolean;
    satellite_cloud_coverage?: number;
    satellite_brightness?: number;
  };
  model_metrics?: {
    mae: number;
    rmse: number;
    r2: number;
    mape: number;
    coverage_80pct: number;
  };
}

// Legacy types (for backward compatibility)
export interface ForecastPoint {
  time: string;
  timestamp: string;
  p10: number;
  p50: number;
  p90: number;
  power_output: number;
}

export interface ForecastResponse {
  location: {
    lat: number;
    lon: number;
  };
  timestamp: string;
  forecasts: ForecastPoint[];
  confidence: number;
  alerts: any[];
  current_irradiance: number;
  current_power_output: number;
  cloud_data?: {
    cloud_map: number[][];
    motion_vectors: Array<{ x: number; y: number }>;
  };
}

// System Status type for dashboard
export interface SystemStatus {
  battery_soc: number;
  diesel_status: 'standby' | 'running' | 'off';
  load_kw: number;
  solar_generation_kw: number;
  grid_import_kw: number;
  uptime_hours: number;
  last_updated: string;
}