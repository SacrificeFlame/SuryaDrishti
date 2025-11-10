# API Endpoints Reference for Frontend

Complete list of all forecast API endpoints you can call from the frontend.

## Base URL
```
http://localhost:8000/api/v1
```
(Or your production URL)

---

## 📊 Forecast Endpoints

### 1. **NGBoost Forecast** (General Purpose)
**Endpoint**: `GET /api/v1/forecast/ngboost`

**Description**: Get 24-hour ahead GHI forecast using NGBoost probabilistic model.

**Query Parameters**:
- `lat` (required): Latitude (float)
- `lon` (required): Longitude (float)
- `horizon_hours` (optional): Forecast horizon in hours (1-48, default: 24)
- `training_days` (optional): Days of historical data for training (30-730, default: 180)
- `retrain` (optional): Force retrain model (boolean, default: false)

**Example Request**:
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/forecast/ngboost?lat=28.7&lon=77.1&horizon_hours=24&training_days=180'
);
const data = await response.json();
```

**Example Response**:
```json
{
  "status": "ok",
  "model": "ngboost",
  "location": {"lat": 28.7, "lon": 77.1},
  "horizon_hours": 24,
  "forecast": [
    {
      "time": "2025-11-09 12:00",
      "timestamp": "2025-11-09T12:00:00+05:30",
      "p10": 638.4,
      "p50": 672.1,
      "p90": 705.8,
      "mean": 672.1,
      "std": 26.3,
      "ghi": 672.1,
      "ghi_clear_sky": 850.2,
      "clear_sky_ratio": 0.79,
      "solar_elevation": 45.3,
      "is_daytime": true
    }
  ],
  "summary": {
    "mean_ghi": 350.5,
    "max_ghi": 672.1,
    "min_ghi": 2.0,
    "avg_uncertainty": 25.3
  },
  "metadata": {
    "data_source": "open-meteo",
    "retrained": false,
    "training_days": 180,
    "n_samples": 24,
    "features_used": 35
  }
}
```

---

### 2. **Hybrid Forecast** (Best Accuracy - Satellite + Weather)
**Endpoint**: `GET /api/v1/forecast/hybrid`

**Description**: Hybrid forecast combining Open-Meteo weather data with satellite cloud imagery.

**Query Parameters**:
- `lat` (required): Latitude (float)
- `lon` (required): Longitude (float)
- `horizon_hours` (optional): Forecast horizon in hours (1-48, default: 24)
- `use_satellite` (optional): Include satellite cloud data (boolean, default: true)
- `training_days` (optional): Days of historical data for training (30-730, default: 180)

**Example Request**:
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/forecast/hybrid?lat=28.7&lon=77.1&use_satellite=true&training_days=180'
);
const data = await response.json();
```

**Example Response**:
```json
{
  "status": "ok",
  "model": "hybrid_ngboost",
  "location": {"lat": 28.7, "lon": 77.1},
  "horizon_hours": 24,
  "forecast": [
    {
      "time": "2025-11-09 12:00",
      "timestamp": "2025-11-09T12:00:00+05:30",
      "p10": 638.4,
      "p50": 672.1,
      "p90": 705.8,
      "mean": 672.1,
      "std": 26.3,
      "ghi": 672.1,
      "ghi_clear_sky": 850.2,
      "clear_sky_ratio": 0.79,
      "solar_elevation": 45.3
    }
  ],
  "summary": {
    "mean_ghi": 350.5,
    "max_ghi": 672.1,
    "min_ghi": 2.0,
    "avg_uncertainty": 25.3
  },
  "satellite": {
    "satellite_available": true,
    "satellite_cloud_coverage": 0.25,
    "satellite_brightness": 0.85
  },
  "model_metrics": {
    "mae": 35.2,
    "rmse": 48.5,
    "r2": 0.89,
    "mape": 8.5,
    "coverage_80pct": 0.82
  },
  "metadata": {
    "data_sources": ["open-meteo", "satellite"],
    "training_days": 180,
    "n_samples": 24,
    "features_used": 37
  }
}
```

---

### 3. **Microgrid Forecast** (Recommended for Microgrids) ⭐
**Endpoint**: `GET /api/v1/forecast/microgrid/{microgrid_id}`

**Description**: Get solar irradiance and power output forecast for a specific microgrid. Converts GHI to power output automatically.

**Path Parameters**:
- `microgrid_id` (required): Microgrid ID (string)

**Query Parameters**:
- `horizon_hours` (optional): Forecast horizon in hours (1-48, default: 24)
- `training_days` (optional): Days of historical data for training (30-730, default: 180)
- `retrain` (optional): Force retrain model (boolean, default: false)

**Example Request**:
```javascript
const microgridId = 'mg_001';
const response = await fetch(
  `http://localhost:8000/api/v1/forecast/microgrid/${microgridId}?horizon_hours=24&training_days=180`
);
const data = await response.json();
```

**Example Response**:
```json
{
  "status": "ok",
  "model": "ngboost_microgrid",
  "microgrid": {
    "id": "mg_001",
    "name": "Village Microgrid",
    "location": {"lat": 28.6139, "lon": 77.2090},
    "capacity_kw": 50.0
  },
  "horizon_hours": 24,
  "forecast": [
    {
      "time": "2025-11-09 12:00",
      "timestamp": "2025-11-09T12:00:00+05:30",
      "ghi": {
        "p10": 638.4,
        "p50": 672.1,
        "p90": 705.8,
        "mean": 672.1,
        "std": 26.3,
        "clear_sky": 850.2,
        "clear_sky_ratio": 0.79
      },
      "power_kw": {
        "p10": 27.1,
        "p50": 28.6,
        "p90": 30.0,
        "mean": 28.6,
        "clear_sky": 36.1
      },
      "energy_kwh": 28.6,
      "solar_elevation": 45.3,
      "is_daytime": true
    }
  ],
  "summary": {
    "ghi": {
      "mean": 350.5,
      "max": 672.1,
      "min": 2.0
    },
    "power_kw": {
      "mean": 14.9,
      "max": 28.6,
      "min": 0.1
    },
    "total_energy_kwh": 357.6,
    "avg_uncertainty": 25.3
  },
  "metadata": {
    "data_source": "open-meteo",
    "retrained": false,
    "training_days": 180,
    "n_samples": 24,
    "features_used": 35
  }
}
```

---

## 🔧 Frontend Integration Examples

### React/TypeScript Example

```typescript
// types.ts
export interface ForecastResponse {
  status: string;
  model: string;
  location: { lat: number; lon: number };
  horizon_hours: number;
  forecast: ForecastPoint[];
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

export interface ForecastPoint {
  time: string;
  timestamp: string;
  p10: number;
  p50: number;
  p90: number;
  mean: number;
  std: number;
  ghi: number;
  ghi_clear_sky?: number;
  clear_sky_ratio?: number;
  solar_elevation?: number;
  is_daytime?: boolean;
}

// api.ts
const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function getNGBoostForecast(
  lat: number,
  lon: number,
  horizonHours: number = 24,
  trainingDays: number = 180
): Promise<ForecastResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    horizon_hours: horizonHours.toString(),
    training_days: trainingDays.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/forecast/ngboost?${params}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getMicrogridForecast(
  microgridId: string,
  horizonHours: number = 24,
  trainingDays: number = 180
) {
  const params = new URLSearchParams({
    horizon_hours: horizonHours.toString(),
    training_days: trainingDays.toString(),
  });

  const response = await fetch(
    `${API_BASE_URL}/forecast/microgrid/${microgridId}?${params}`
  );
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getHybridForecast(
  lat: number,
  lon: number,
  useSatellite: boolean = true,
  horizonHours: number = 24
) {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    horizon_hours: horizonHours.toString(),
    use_satellite: useSatellite.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/forecast/hybrid?${params}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}
```

### React Hook Example

```typescript
// useForecast.ts
import { useState, useEffect } from 'react';
import { getNGBoostForecast, getMicrogridForecast } from './api';

export function useForecast(lat: number, lon: number) {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchForecast() {
      try {
        setLoading(true);
        const data = await getNGBoostForecast(lat, lon);
        setForecast(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchForecast();
  }, [lat, lon]);

  return { forecast, loading, error };
}

export function useMicrogridForecast(microgridId: string) {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchForecast() {
      try {
        setLoading(true);
        const data = await getMicrogridForecast(microgridId);
        setForecast(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    if (microgridId) {
      fetchForecast();
    }
  }, [microgridId]);

  return { forecast, loading, error };
}
```

### Component Example

```tsx
// ForecastChart.tsx
import { useMicrogridForecast } from './useForecast';

export function ForecastChart({ microgridId }: { microgridId: string }) {
  const { forecast, loading, error } = useMicrogridForecast(microgridId);

  if (loading) return <div>Loading forecast...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!forecast) return null;

  return (
    <div>
      <h2>Forecast for {forecast.microgrid.name}</h2>
      <p>Total Energy: {forecast.summary.total_energy_kwh.toFixed(1)} kWh</p>
      <p>Mean Power: {forecast.summary.power_kw.mean.toFixed(1)} kW</p>
      
      <div>
        {forecast.forecast.map((point) => (
          <div key={point.time}>
            <span>{point.time}</span>
            <span>GHI: {point.ghi.mean.toFixed(0)} W/m²</span>
            <span>Power: {point.power_kw.mean.toFixed(1)} kW</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 📝 Quick Reference

### Endpoint Comparison

| Endpoint | Best For | Returns Power? | Uses Satellite? |
|----------|----------|----------------|-----------------|
| `/ngboost` | General forecasting | ❌ No | ❌ No |
| `/hybrid` | Maximum accuracy | ❌ No | ✅ Yes |
| `/microgrid/{id}` | Microgrids | ✅ Yes | ❌ No |

### Recommended Usage

- **For Microgrids**: Use `/microgrid/{id}` - automatically converts to power
- **For General Use**: Use `/ngboost` - fast and reliable
- **For Best Accuracy**: Use `/hybrid` - combines weather + satellite

---

## ⚠️ Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Microgrid not found (for microgrid endpoint)
- `500 Internal Server Error`: Server error

**Error Response Format**:
```json
{
  "detail": "Error message here"
}
```

---

## 🔗 Related Endpoints

### Get Microgrid Info
```
GET /api/v1/microgrid/{microgrid_id}
```

### Get Sensor Readings
```
GET /api/v1/sensors/{microgrid_id}/latest
GET /api/v1/sensors/{microgrid_id}/history?limit=100
```

### Get Alerts
```
GET /api/v1/alerts/{microgrid_id}?limit=20
```

---

## 📚 Full API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with Swagger UI.






