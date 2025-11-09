# Frontend Integration Guide - SuryaDrishti Updates

## Overview

This document describes all the new features and API endpoints that have been implemented and how to integrate them into the frontend.

## Table of Contents

1. [Battery Scheduler & SOC Trend Fixes](#battery-scheduler--soc-trend-fixes)
2. [SMS/Push Notifications](#sms-push-notifications)
3. [Irrigation Pump Automation](#irrigation-pump-automation)
4. [Energy Loss Prevention Reports](#energy-loss-prevention-reports)
5. [PostgreSQL Migration Support](#postgresql-migration-support)
6. [API Endpoints Reference](#api-endpoints-reference)

---

## Battery Scheduler & SOC Trend Fixes

### What Changed

The battery scheduler now uses the proper `SchedulerEngine` with:
- Real battery capacity and charge/discharge rates from microgrid configuration
- Actual device loads from the database
- Proper SOC calculations based on battery efficiency and capacity
- Integration with forecast data

### Frontend Impact

**No changes required** - The existing `/api/v1/forecast/schedule` endpoint now returns more accurate data:

```typescript
// The schedule endpoint now returns:
{
  status: 'ok',
  data: {
    schedule: [
      {
        step: 1,
        time: '2025-11-09 14:00:00',
        solar_kW: 45.2,
        load_kW: 18.5,
        charging_kW: 10.0,  // Now uses actual battery max charge rate
        discharging_kW: 0,
        soc_percent: 52.3  // Now calculated using proper battery capacity
      },
      // ...
    ],
    forecast_kW: [45.2, 48.1, ...],  // Aligned with actual forecast
    weather: [...],
    soc_target: 0.8
  }
}
```

### Battery SOC Trend Chart

The SOC Trend chart now displays accurate values because:
- SOC is calculated using actual battery capacity (kWh)
- Charge/discharge rates respect battery limits
- Efficiency losses are accounted for (95% round-trip)

**No frontend changes needed** - the chart automatically uses the improved data.

---

## SMS/Push Notifications

### New API Endpoints

#### 1. Get Notification Preferences
```http
GET /api/v1/notifications/preferences/{microgrid_id}
```

**Response:**
```json
{
  "microgrid_id": "microgrid_001",
  "phone_number": "+919876543210",
  "email": "operator@example.com",
  "enable_sms": true,
  "enable_email": false,
  "enable_critical_alerts": true,
  "enable_warning_alerts": true,
  "enable_info_alerts": false,
  "enable_forecast_updates": false
}
```

#### 2. Update Notification Preferences
```http
POST /api/v1/notifications/preferences/{microgrid_id}
Content-Type: application/json

{
  "phone_number": "+919876543210",
  "email": "operator@example.com",
  "enable_sms": true,
  "enable_email": false,
  "enable_critical_alerts": true,
  "enable_warning_alerts": true,
  "enable_info_alerts": false,
  "enable_forecast_updates": false
}
```

#### 3. Send Test Notification
```http
POST /api/v1/notifications/send-test/{microgrid_id}
```

### Frontend Integration

#### TypeScript Types

```typescript
// Add to types/forecast.ts or create types/notifications.ts
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
```

#### API Service Functions

```typescript
// Add to lib/api-client.ts

export async function getNotificationPreferences(microgridId: string): Promise<NotificationPreferences> {
  const response = await fetch(
    `http://localhost:8000/api/v1/notifications/preferences/${microgridId}`
  );
  if (!response.ok) throw new Error('Failed to fetch notification preferences');
  return response.json();
}

export async function updateNotificationPreferences(
  microgridId: string,
  preferences: NotificationPreferenceRequest
): Promise<NotificationPreferences> {
  const response = await fetch(
    `http://localhost:8000/api/v1/notifications/preferences/${microgridId}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(preferences)
    }
  );
  if (!response.ok) throw new Error('Failed to update notification preferences');
  return response.json();
}

export async function sendTestNotification(microgridId: string): Promise<{ status: string }> {
  const response = await fetch(
    `http://localhost:8000/api/v1/notifications/send-test/${microgridId}`,
    { method: 'POST' }
  );
  if (!response.ok) throw new Error('Failed to send test notification');
  return response.json();
}
```

#### UI Component Example

```typescript
// components/settings/NotificationSettings.tsx
'use client';

import { useState, useEffect } from 'react';
import { getNotificationPreferences, updateNotificationPreferences, sendTestNotification } from '@/lib/api-client';

export default function NotificationSettings({ microgridId }: { microgridId: string }) {
  const [prefs, setPrefs] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPreferences();
  }, [microgridId]);

  const loadPreferences = async () => {
    try {
      const data = await getNotificationPreferences(microgridId);
      setPrefs(data);
    } catch (error) {
      console.error('Failed to load preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!prefs) return;
    try {
      await updateNotificationPreferences(microgridId, prefs);
      alert('Preferences saved successfully!');
    } catch (error) {
      alert('Failed to save preferences');
    }
  };

  const handleTest = async () => {
    try {
      await sendTestNotification(microgridId);
      alert('Test notification sent!');
    } catch (error) {
      alert('Failed to send test notification');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!prefs) return <div>Error loading preferences</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Notification Settings</h2>
      
      <div>
        <label>Phone Number (E.164 format, e.g., +919876543210)</label>
        <input
          type="tel"
          value={prefs.phone_number || ''}
          onChange={(e) => setPrefs({ ...prefs, phone_number: e.target.value })}
          className="w-full px-4 py-2 border rounded"
        />
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={prefs.enable_sms}
            onChange={(e) => setPrefs({ ...prefs, enable_sms: e.target.checked })}
          />
          Enable SMS Notifications
        </label>
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={prefs.enable_critical_alerts}
            onChange={(e) => setPrefs({ ...prefs, enable_critical_alerts: e.target.checked })}
          />
          Critical Alerts
        </label>
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={prefs.enable_warning_alerts}
            onChange={(e) => setPrefs({ ...prefs, enable_warning_alerts: e.target.checked })}
          />
          Warning Alerts
        </label>
      </div>

      <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded">
        Save Preferences
      </button>

      <button onClick={handleTest} className="px-4 py-2 bg-green-600 text-white rounded">
        Send Test Notification
      </button>
    </div>
  );
}
```

### Environment Variables

Add to `.env` file:
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890  # Your Twilio phone number
```

---

## Irrigation Pump Automation

### What Changed

The scheduler engine now automatically delays irrigation pumps when:
- Power drop > 25% is forecasted in next 30-60 minutes
- Battery SOC < 40%
- Or power drop > 40% regardless of SOC

### Frontend Impact

**No API changes** - The automation happens automatically in the scheduler. However, you can display irrigation pump delays in the schedule:

```typescript
// The schedule endpoint now includes device information
{
  schedule: [
    {
      step: 1,
      time: '...',
      solar_kW: 45.2,
      load_kW: 18.5,
      devices: [
        { id: 'pump_1', name: 'Irrigation Pump 1', power_kw: 5.0 },
        // Irrigation pumps may be missing if delayed
      ]
    }
  ]
}
```

### Displaying Delayed Pumps

You can check if irrigation pumps are missing from the schedule to indicate they were delayed:

```typescript
// In your schedule component
const irrigationPumps = devices.filter(d => 
  d.device_type === 'irrigation' || 
  d.name.toLowerCase().includes('pump')
);

const activePumps = scheduleSlot.devices.filter(d =>
  irrigationPumps.some(p => p.id === d.id)
);

if (irrigationPumps.length > activePumps.length) {
  // Some pumps were delayed
  const delayedPumps = irrigationPumps.filter(p =>
    !activePumps.some(a => a.id === p.id)
  );
  // Display delay message
}
```

---

## Energy Loss Prevention Reports

### New API Endpoints

#### 1. Energy Loss Report
```http
GET /api/v1/reports/energy-loss/{microgrid_id}?start_date=2025-11-01&end_date=2025-11-08
```

**Response:**
```json
{
  "microgrid_id": "microgrid_001",
  "period": {
    "start_date": "2025-11-01",
    "end_date": "2025-11-08"
  },
  "metrics": {
    "total_forecast_energy_kwh": 1250.5,
    "total_actual_energy_kwh": 1180.2,
    "energy_saved_kwh": 70.3,
    "prevented_outages": 3,
    "battery_cycles_saved": 1.5,
    "alerts_triggered": 12,
    "forecast_accuracy_percent": 94.2
  },
  "summary": {
    "total_alerts": 12,
    "critical_alerts": 2,
    "warning_alerts": 8,
    "actions_taken": 10
  }
}
```

#### 2. Performance Report
```http
GET /api/v1/reports/performance/{microgrid_id}?days=7
```

**Response:**
```json
{
  "microgrid_id": "microgrid_001",
  "period_days": 7,
  "metrics": {
    "forecasts_generated": 168,
    "sensor_readings": 2016,
    "alerts_triggered": 12,
    "system_uptime_percent": 98.5,
    "forecast_accuracy_mae": 15.2
  },
  "alerts_by_severity": {
    "critical": 2,
    "warning": 8,
    "info": 2
  }
}
```

### Frontend Integration

A React component has been created at `frontend/src/components/dashboard/EnergyLossReport.tsx`. To use it:

```typescript
// In your dashboard or reports page
import EnergyLossReport from '@/components/dashboard/EnergyLossReport';

<EnergyLossReport microgridId="microgrid_001" />
```

### API Service Functions

```typescript
// Add to lib/api-client.ts

export async function getEnergyLossReport(
  microgridId: string,
  startDate: string,
  endDate: string
): Promise<EnergyLossReport> {
  const response = await fetch(
    `http://localhost:8000/api/v1/reports/energy-loss/${microgridId}?start_date=${startDate}&end_date=${endDate}`
  );
  if (!response.ok) throw new Error('Failed to fetch energy loss report');
  return response.json();
}

export async function getPerformanceReport(
  microgridId: string,
  days: number = 7
): Promise<PerformanceReport> {
  const response = await fetch(
    `http://localhost:8000/api/v1/reports/performance/${microgridId}?days=${days}`
  );
  if (!response.ok) throw new Error('Failed to fetch performance report');
  return response.json();
}
```

---

## PostgreSQL Migration Support

### What Changed

The system now supports both SQLite (development) and PostgreSQL (production). The database URL is automatically detected from environment variables.

### Environment Variables

```bash
# For PostgreSQL (production)
DATABASE_URL=postgresql://user:password@localhost:5432/suryadrishti
# OR
POSTGRES_URL=postgresql://user:password@localhost:5432/suryadrishti

# For SQLite (development - default)
SQLITE_DB_PATH=suryादrishti.db
```

### Frontend Impact

**No frontend changes required** - Database migration is handled entirely on the backend.

### Migration Script

To migrate from SQLite to PostgreSQL:

```python
from app.core.database_migration import migrate_to_postgresql

migrate_to_postgresql(
    source_db_path='suryादrishti.db',
    target_postgres_url='postgresql://user:password@localhost:5432/suryadrishti'
)
```

---

## API Endpoints Reference

### Updated Endpoints

#### `/api/v1/forecast/schedule` (POST)
- **Changed**: Now uses proper scheduler engine with real battery parameters
- **Response format**: Same, but data is more accurate

### New Endpoints

#### Notification Endpoints
- `GET /api/v1/notifications/preferences/{microgrid_id}` - Get preferences
- `POST /api/v1/notifications/preferences/{microgrid_id}` - Update preferences
- `POST /api/v1/notifications/send-test/{microgrid_id}` - Send test SMS

#### Report Endpoints
- `GET /api/v1/reports/energy-loss/{microgrid_id}` - Energy loss report
- `GET /api/v1/reports/performance/{microgrid_id}` - Performance report

---

## Summary of Changes

### ✅ Completed Features

1. **Battery Scheduler Fixed**
   - Uses real battery capacity and charge/discharge rates
   - Proper SOC calculations
   - Integrated with forecast data

2. **Battery SOC Trend Fixed**
   - Displays accurate SOC values
   - Uses proper battery efficiency calculations

3. **Power Forecast Graph Fixed**
   - Aligned with dashboard forecast data
   - Uses actual forecast values

4. **SMS/Push Notifications**
   - Twilio integration
   - Notification preferences API
   - Automatic alert notifications

5. **Irrigation Pump Automation**
   - Automatic delay based on forecast
   - Integrated into scheduler engine

6. **Energy Loss Prevention Reports**
   - API endpoints created
   - React component created
   - Metrics and analytics

7. **PostgreSQL Migration Support**
   - Automatic database detection
   - Migration utilities

### 📝 Frontend Tasks

1. **Add Notification Settings Page**
   - Use `NotificationSettings` component example above
   - Add route: `/settings/notifications`

2. **Add Reports Page**
   - Use `EnergyLossReport` component
   - Add route: `/reports/energy-loss`

3. **Update Schedule Display**
   - Show irrigation pump delays
   - Display device information in schedule

4. **Environment Variables**
   - Add Twilio credentials to `.env.local` (frontend doesn't need them, but document for backend)

---

## Testing Checklist

- [ ] Test battery scheduler with different battery capacities
- [ ] Verify SOC Trend chart displays correct values
- [ ] Test Power Forecast Graph alignment
- [ ] Configure Twilio and test SMS notifications
- [ ] Test notification preferences API
- [ ] Verify irrigation pump delays in schedule
- [ ] Test energy loss report API
- [ ] Display reports in frontend
- [ ] Test PostgreSQL migration (if applicable)

---

## Next Steps

1. **Frontend Implementation**
   - Create notification settings page
   - Add reports page
   - Update schedule display for irrigation delays

2. **Backend Configuration**
   - Set up Twilio account and credentials
   - Configure notification preferences for microgrids
   - Set up PostgreSQL (if moving to production)

3. **Testing**
   - Test all new endpoints
   - Verify SMS notifications work
   - Test irrigation pump automation
   - Validate reports accuracy

---

## Support

For questions or issues, refer to:
- API documentation: `http://localhost:8000/docs`
- Backend logs: Check console output
- Database: Check `suryादrishti.db` (SQLite) or PostgreSQL database
