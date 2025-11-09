/**
 * Reports API Type Definitions
 */

export interface EnergyLossReport {
  microgrid_id: string;
  period: {
    start_date: string;
    end_date: string;
  };
  metrics: {
    total_forecast_energy_kwh: number;
    total_actual_energy_kwh: number;
    energy_saved_kwh: number;
    prevented_outages: number;
    battery_cycles_saved: number;
    alerts_triggered: number;
    forecast_accuracy_percent: number;
  };
  summary: {
    total_alerts: number;
    critical_alerts: number;
    warning_alerts: number;
    actions_taken: number;
  };
}

export interface PerformanceReport {
  microgrid_id: string;
  period_days: number;
  metrics: {
    forecasts_generated: number;
    sensor_readings: number;
    alerts_triggered: number;
    system_uptime_percent: number;
    forecast_accuracy_mae: number;
  };
  alerts_by_severity: {
    critical: number;
    warning: number;
    info: number;
  };
}

