/**
 * Notification API Type Definitions
 */

export interface NotificationPreferences {
  microgrid_id: string;
  phone_number: string | null;
  email: string | null;
  enable_sms: boolean;
  enable_email: boolean;
  enable_critical_alerts: boolean;
  enable_warning_alerts: boolean;
  enable_info_alerts: boolean;
  enable_forecast_updates: boolean;
}

export interface NotificationPreferenceRequest {
  phone_number?: string | null;
  email?: string | null;
  enable_sms?: boolean;
  enable_email?: boolean;
  enable_critical_alerts?: boolean;
  enable_warning_alerts?: boolean;
  enable_info_alerts?: boolean;
  enable_forecast_updates?: boolean;
}

