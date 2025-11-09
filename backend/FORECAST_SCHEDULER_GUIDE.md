# Forecast & Scheduler Implementation Guide

## Overview

This guide explains the forecast and scheduler system that uses the external forecast API (`http://127.0.0.1:8000/api/run`) for all solar forecasting and energy scheduling operations.

The forecast system uses an **NGBoost probabilistic model** that generates hourly forecasts with uncertainty estimates (P10, P50, P90), which are then converted to power output and displayed in the frontend.

## Architecture

### Components

1. **External Forecast Service** (`app/services/external_forecast_service.py`)
   - Handles all communication with the external API
   - Parses and converts external API responses
   - Ensures data format consistency

2. **Forecast Endpoints** (`app/api/v1/forecast_microgrid.py`, `app/api/v1/forecast.py`)
   - `/api/v1/forecast/microgrid/{microgrid_id}` - Main forecast endpoint for dashboard
   - `/api/v1/forecast/schedule` - Schedule format endpoint for forecast-schedule page

3. **Scheduler Endpoint** (`app/api/v1/schedules.py`)
   - `/api/v1/microgrid/{microgrid_id}/schedules/generate` - Generates optimized energy schedules

## External API Integration

### API Details

- **URL**: `http://127.0.0.1:8000/api/run`
- **Method**: POST
- **Headers**:
  - `Content-Type: application/json`
  - `x-api-key: aryan1234%^&*()`
- **Request Body**: `{"source": "hybrid"}`
- **Timeout**: 30 seconds

### Forecast Generation Process

The external API uses an **NGBoost probabilistic model** that:

1. **Fetches Historical Weather Data** (Open-Meteo API)
   - Last 180 days of weather data
   - Features: temperature, cloud cover, humidity, pressure, wind speed, etc.

2. **Trains/Updates NGBoost Model**
   - Gradient boosting for probabilistic prediction
   - Learns patterns from historical data
   - Generates uncertainty estimates

3. **Generates Hourly Forecasts**
   - For each hour in the next 24 hours
   - Produces **probabilistic predictions**:
     - **P10** (10th percentile): Pessimistic scenario (10% chance of being lower)
     - **P50** (50th percentile): Most likely (median)
     - **P90** (90th percentile): Optimistic scenario (90% chance of being lower)
   - Also calculates **mean** and **standard deviation** (uncertainty)

### How It Works

```python
# 1. Fetch from external API
external_data = await fetch_forecast_from_external_api(source="hybrid")

# 2. Parse response (handles multiple formats)
parsed_forecast = parse_external_api_response(external_data)

# 3. Convert to internal format
microgrid_forecast = convert_to_microgrid_forecast_format(
    parsed_forecast,
    microgrid_id,
    lat,
    lon,
    capacity_kw
)
```

## Key Files

### 1. `app/services/external_forecast_service.py`

**Purpose**: Central service for external API communication

**Key Functions**:

- `fetch_forecast_from_external_api(source="hybrid")`
  - Calls external API with proper headers
  - Handles timeouts and errors
  - Returns raw API response

- `parse_external_api_response(external_data)`
  - Handles multiple response formats:
    - `{"forecast": [...]}`
    - `{"data": {"forecast": [...]}}`
    - `{"output": {"forecast": [...]}}`
    - `{"data": [...]}` (array directly)
  - Returns standardized format with `forecast` key

- `convert_to_microgrid_forecast_format(...)`
  - Converts external API format to `MicrogridForecastResponse`
  - Handles GHI and power data extraction
  - Calculates daytime/nighttime status
  - Ensures nighttime values are zero
  - Applies fallback calculations for daytime zero values

**Response Format**:
```python
{
    "status": "ok",
    "model": "external_api_hybrid",
    "microgrid": {
        "id": "microgrid_001",
        "name": "Microgrid microgrid_001",
        "location": {"lat": 28.4595, "lon": 77.0266},
        "capacity_kw": 50.0
    },
    "horizon_hours": 24,
    "forecast": [
        {
            "time": "2025-01-09 14:00",
            "timestamp": "2025-01-09T14:00:00+00:00",
            "ghi": {
                "p10": 400.0,
                "p50": 500.0,
                "p90": 600.0,
                "mean": 500.0,
                "std": 50.0
            },
            "power_kw": {
                "p10": 30.0,
                "p50": 37.5,
                "p90": 45.0,
                "mean": 37.5
            },
            "energy_kwh": 37.5,
            "solar_elevation": 45.0,
            "is_daytime": True
        },
        # ... more forecast points
    ],
    "summary": {
        "ghi": {"mean": 450.0, "max": 800.0, "min": 0.0},
        "power_kw": {"mean": 33.75, "max": 60.0, "min": 0.0},
        "total_energy_kwh": 810.0,
        "avg_uncertainty": 50.0
    },
    "metadata": {
        "data_source": "external_api_hybrid",
        "retrained": False,
        "training_days": 0,
        "n_samples": 24,
        "features_used": 0
    }
}
```

### 2. `app/api/v1/forecast_microgrid.py`

**Endpoint**: `GET /api/v1/forecast/microgrid/{microgrid_id}`

**Purpose**: Provides forecast data for the main dashboard

**Query Parameters**:
- `horizon_hours` (1-48): Forecast horizon in hours (default: 24)
- `training_days` (30-730): Not used with external API (kept for compatibility)
- `retrain` (bool): Not used with external API (kept for compatibility)

**Flow**:
1. Get microgrid details from database
2. Call external API via service
3. Parse and convert response
4. Limit to requested `horizon_hours`
5. Return `MicrogridForecastResponse` format

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/forecast/microgrid/microgrid_001?horizon_hours=24"
```

**Example Response**: See format above

### 3. `app/api/v1/forecast.py` - Schedule Endpoint

**Endpoint**: `POST /api/v1/forecast/schedule`

**Purpose**: Provides forecast data in schedule format for the forecast-schedule page

**Query Parameters**:
- `forecast_hours` (1-48): Forecast horizon in hours (default: 12)
- `microgrid_id`: Microgrid identifier (default: "microgrid_001")

**Flow**:
1. Get microgrid info from database
2. Call external API via service
3. Convert to schedule format:
   - `schedule`: Array of time slots with solar, load, battery, grid data
   - `forecast_kW`: Array of solar power values
   - `weather`: Array of weather data (GHI, cloud, POA)

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/forecast/schedule?forecast_hours=12&microgrid_id=microgrid_001"
```

**Example Response**:
```json
{
    "status": "ok",
    "data": {
        "meta": {
            "generated_at": "2025-01-09T11:40:34.123Z",
            "location": {"lat": 28.4595, "lon": 77.0266},
            "forecast_horizon_hours": 12,
            "source": "external_api_hybrid"
        },
        "schedule": [
            {
                "step": 1,
                "time": "2025-01-09 13:30:00",
                "solar_kW": 35.5,
                "load_kW": 15.0,
                "charging_kW": 20.5,
                "discharging_kW": 0,
                "soc_percent": 52.5
            },
            // ... more schedule items
        ],
        "soc_target": 0.8,
        "forecast_kW": [35.5, 38.2, 40.1, ...],
        "weather": [
            {
                "time": "2025-01-09 13:30:00",
                "ghi": 500.0,
                "cloud": 0,
                "poa_global": 500.0,
                "predicted_kW": 35.5
            },
            // ... more weather items
        ]
    }
}
```

### 4. `app/api/v1/schedules.py` - Schedule Generation

**Endpoint**: `POST /api/v1/microgrid/{microgrid_id}/schedules/generate`

**Purpose**: Generates optimized energy schedules using the scheduler engine

**Request Body**:
```json
{
    "date": "2025-01-09",
    "use_forecast": true,
    "optimization_mode": "cost"
}
```

**Flow**:
1. Get microgrid, devices, and configuration from database
2. If `use_forecast` is true:
   - Call external API via service
   - Convert to scheduler format
   - Expand hourly data to 10-minute intervals
3. Run scheduler engine with forecast data
4. Save schedule to database
5. Return schedule with optimization metrics

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/microgrid/microgrid_001/schedules/generate" \
  -H "Content-Type: application/json" \
  -d '{"use_forecast": true, "optimization_mode": "cost"}'
```

## Data Flow

### Complete Flow: From External API to Frontend

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend Dashboard                                          │
│  - Displays forecast with 5-minute interval labels          │
│  - Shows P10/P50/P90 probabilistic values                   │
│  - Calculates confidence from uncertainty                   │
└────────┬────────────────────────────────────────────────────┘
         │
         │ GET /api/v1/forecast/microgrid/microgrid_001
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  forecast_microgrid.py                                      │
│  - Get microgrid from DB (lat, lon, capacity)              │
│  - Call external API service                                │
│  - Convert format to MicrogridForecastResponse             │
│  - Return hourly forecasts with P10/P50/P90                │
└────────┬────────────────────────────────────────────────────┘
         │
         │ fetch_forecast_from_external_api(source="hybrid")
         ▼
┌─────────────────────────────────────────────────────────────┐
│  external_forecast_service.py                               │
│  - POST to http://127.0.0.1:8000/api/run                   │
│  - Headers: x-api-key, Content-Type                        │
│  - Body: {"source": "hybrid"}                              │
│  - Parse response (handles multiple formats)               │
│  - Convert to internal format                              │
│  - Apply GHI to power conversion                           │
│  - Validate daytime/nighttime                              │
└────────┬────────────────────────────────────────────────────┘
         │
         │ HTTP POST (30s timeout)
         ▼
┌─────────────────────────────────────────────────────────────┐
│  External Forecast API                                       │
│  http://127.0.0.1:8000/api/run                            │
│                                                             │
│  1. Fetch Historical Weather (Open-Meteo API)              │
│     - Last 180 days of weather data                        │
│     - Features: temp, cloud, humidity, pressure, wind       │
│                                                             │
│  2. Train/Update NGBoost Model                             │
│     - Gradient boosting for probabilistic prediction      │
│     - Learns patterns from historical data                 │
│     - Generates uncertainty estimates                      │
│                                                             │
│  3. Generate Hourly Forecasts                              │
│     - For each hour in next 24 hours                      │
│     - Returns: P10, P50, P90, mean, std                    │
│     - GHI values in W/m²                                   │
└─────────────────────────────────────────────────────────────┘
         │
         │ Response: {"forecast": [{timestamp, ghi: {p10, p50, p90, mean, std}, ...}]}
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend Processing                                         │
│                                                             │
│  1. Parse external API response                            │
│  2. Convert GHI to Power (ghi_to_power function)           │
│     - Accounts for: system losses (15%), temp (5%),        │
│       pollution (5%), soiling (3%)                        │
│  3. Validate daytime/nighttime                             │
│     - Daytime (6 AM - 7 PM IST): ensure non-zero values    │
│     - Nighttime: set all values to zero                    │
│  4. Format as MicrogridForecastResponse                    │
└────────┬────────────────────────────────────────────────────┘
         │
         │ Response: MicrogridForecastResponse
         │ {forecast: [{ghi: {p10, p50, p90, mean, std},     │
         │              power_kw: {p10, p50, p90, mean},    │
         │              timestamp, is_daytime, ...}]}
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend Transformation                                    │
│                                                             │
│  1. Take first 10 hourly forecast points                   │
│  2. Transform to display format                           │
│     - Convert timestamps to clock times (e.g., "6:39 AM")  │
│     - Extract P10/P50/P90 from ghi and power_kw            │
│  3. Calculate confidence: 1 - (avg_uncertainty / 1000)     │
│  4. Display as 5-minute interval labels                   │
│     (Note: Actually hourly data, displayed with time labels)│
└─────────────────────────────────────────────────────────────┘
```

### Key Transformations

1. **External API → Backend**: Raw forecast data with GHI values
2. **Backend Processing**: GHI → Power conversion, daytime validation
3. **Backend → Frontend**: Structured `MicrogridForecastResponse` format
4. **Frontend Display**: Hourly data displayed as time-based intervals

## Daytime/Nighttime Handling

### Critical Logic

The system ensures **daytime values are never zero** and **nighttime values are always zero**.

**Daytime Definition**: 6:00 AM to 7:00 PM IST (360 to 1140 minutes)

**Process**:
1. Convert timestamp to IST timezone
2. Check if time is within daytime window
3. If daytime and values are zero/low:
   - Apply fallback calculation based on time of day
   - Solar curve: peaks at noon (12:00 PM), decays over 6 hours
   - Minimum GHI: 50 W/m² (twilight value)
4. If nighttime:
   - Set all GHI and power values to zero
   - Set `is_daytime: false`

**Fallback Calculation**:
```python
# Calculate solar factor (0-1) based on distance from noon
hour_offset_from_noon = abs(total_minutes_ist - 720) / 60.0  # 720 = noon in minutes
solar_factor = max(0, 1 - (hour_offset_from_noon / 6))

# Apply to GHI
ghi = 650.0 * solar_factor  # Peak GHI at noon
if ghi < 50:
    ghi = 50.0  # Minimum twilight value

# Convert to power
power_kw = ghi_to_power(ghi, capacity_kw)
```

## GHI to Power Conversion

For each forecast point, the system converts **GHI (W/m²)** to **Power (kW)** using a physics-based formula:

```python
def ghi_to_power(ghi_w_m2, capacity_kw, system_losses=0.15, 
                 temperature_derating=0.05, pollution_factor=0.95, 
                 soiling_factor=0.97):
    """
    Convert GHI (W/m²) to Power (kW) with realistic loss factors.
    
    Args:
        ghi_w_m2: Global Horizontal Irradiance in W/m²
        capacity_kw: Solar panel capacity in kW
        system_losses: System losses (default: 15%)
        temperature_derating: Temperature losses (default: 5%)
        pollution_factor: Air pollution factor for Delhi (default: 95%)
        soiling_factor: Panel soiling factor (default: 97%)
    
    Returns:
        Power output in kW (clamped between 0 and capacity_kw)
    """
    power_kw = (
        (ghi_w_m2 / 1000.0) * 
        capacity_kw * 
        (1 - system_losses) *      # 15% system losses
        (1 - temperature_derating) * # 5% temperature losses
        pollution_factor *          # 95% (Delhi pollution)
        soiling_factor              # 97% (panel soiling)
    )
    return max(0.0, min(power_kw, capacity_kw))
```

**Example Calculation**:
- GHI: 850 W/m²
- Capacity: 50 kW
- Power = (850/1000) × 50 × 0.85 × 0.95 × 0.95 × 0.97 = **40.5 kW**

**Loss Factors Explained**:
- **System Losses (15%)**: Inverter efficiency, wiring losses, etc.
- **Temperature Derating (5%)**: Panel efficiency decreases with heat
- **Pollution Factor (95%)**: Delhi's air pollution reduces irradiance
- **Soiling Factor (97%)**: Dust and dirt on panels reduce efficiency

## Frontend Display Transformation

### Hourly to 5-Minute Intervals

The backend generates **hourly forecasts**, but the frontend displays them as **5-minute intervals**:

```typescript
// Frontend takes first 10 forecast points (hourly)
const forecastPoints = microgridForecast.forecast.slice(0, 10);

// Transforms each point
forecasts = forecastPoints.map((point, idx) => {
  const pointTime = new Date(point.timestamp);
  const minutesFromNow = Math.round((pointTime - now) / (1000 * 60));
  
  // Display as actual clock time (e.g., "6:39 AM", "7:00 AM")
  const timeLabel = pointTime.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit', 
    hour12: true 
  });
  
  return {
    time: timeLabel,              // Actual clock time
    p10: point.ghi.p10,           // From NGBoost model
    p50: point.ghi.p50,           // From NGBoost model
    p90: point.ghi.p90,           // From NGBoost model
    power_output: point.power_kw.mean  // Calculated from GHI
  };
});
```

**Note**: The time labels (e.g., "6:39 AM", "7:00 AM") are calculated from the actual timestamps, so they represent when each forecast point is predicted for, not necessarily exactly 5 minutes apart. The first 10 hourly points give a **60-minute (1-hour) view** of the forecast.

### Confidence Calculation

The **confidence percentage** (e.g., 87%) is calculated from the forecast uncertainty:

```typescript
confidence = 1 - (avg_uncertainty / 1000)
```

Where `avg_uncertainty` is the average standard deviation across all forecast points.

**Example**:
- Average uncertainty: 130 W/m²
- Confidence = 1 - (130/1000) = 0.87 = **87%**

### Current Values Priority

The **Current Irradiance** and **Power Output** displayed on the dashboard come from:

1. **First Priority**: Latest sensor reading from the microgrid (real-time data)
2. **Second Priority**: First forecast point (next hour's prediction)
3. **Fallback**: Zero (if it's nighttime)

This ensures the dashboard always shows the most up-to-date information available.

## Error Handling

### External API Errors

**Timeout (30 seconds)**:
- Logs error
- Returns HTTP 500 with error message
- Frontend should handle gracefully

**HTTP Errors (4xx, 5xx)**:
- Logs status code and response
- Returns HTTP 500 with error details

**Invalid Response Format**:
- Logs available keys in response
- Raises `ValueError` with helpful message
- Returns HTTP 500

**Empty Forecast**:
- Raises `ValueError`
- Returns HTTP 500

### Logging

All operations are logged with appropriate levels:
- `INFO`: Successful operations, data flow
- `WARNING`: Fallback calculations, missing data
- `ERROR`: API failures, parsing errors
- `DEBUG`: Detailed data inspection

## Testing

### Test External API Connection

```bash
# Test the external API directly
curl -X POST "http://127.0.0.1:8000/api/run" \
  -H "x-api-key: aryan1234%^&*()" \
  -H "Content-Type: application/json" \
  -d '{"source":"hybrid"}' | jq
```

### Test Forecast Endpoint

```bash
# Test microgrid forecast
curl "http://localhost:8000/api/v1/forecast/microgrid/microgrid_001?horizon_hours=12"

# Test schedule endpoint
curl -X POST "http://localhost:8000/api/v1/forecast/schedule?forecast_hours=12"
```

### Test Scheduler

```bash
# Generate schedule
curl -X POST "http://localhost:8000/api/v1/microgrid/microgrid_001/schedules/generate" \
  -H "Content-Type: application/json" \
  -d '{"use_forecast": true}'
```

## Configuration

### External API Settings

Located in `app/services/external_forecast_service.py`:

```python
EXTERNAL_API_URL = "http://127.0.0.1:8000/api/run"
EXTERNAL_API_KEY = "aryan1234%^&*()"
REQUEST_TIMEOUT = 30.0  # seconds
```

**To Change API URL**:
1. Update `EXTERNAL_API_URL` in `external_forecast_service.py`
2. Restart backend server

## Response Format Compatibility

### External API Response Formats Supported

The parser handles these formats:

1. **Direct forecast**:
   ```json
   {"forecast": [...]}
   ```

2. **Nested in data**:
   ```json
   {"data": {"forecast": [...]}}
   ```

3. **Nested in output**:
   ```json
   {"output": {"forecast": [...]}}
   ```

4. **Array directly in data**:
   ```json
   {"data": [...]}
   ```

5. **Array directly in output**:
   ```json
   {"output": [...]}
   ```

### Forecast Point Format Expected

Each forecast point should have:
- `timestamp` or `time`: ISO format timestamp
- `ghi`: Number or `{"mean": ..., "p10": ..., "p90": ...}`
- `power_kw` (optional): Number or `{"mean": ..., "p10": ..., "p90": ...}`
- `solar_elevation` (optional): Number in degrees
- `is_daytime` (optional): Boolean

**Example External API Response**:
```json
{
    "forecast": [
        {
            "timestamp": "2025-01-09T14:00:00Z",
            "ghi": {"mean": 500.0, "p10": 400.0, "p90": 600.0},
            "power_kw": {"mean": 37.5},
            "solar_elevation": 45.0,
            "is_daytime": true
        }
    ]
}
```

## Troubleshooting

### Issue: "External API response doesn't contain 'forecast' key"

**Cause**: External API returned unexpected format

**Solution**:
1. Check external API response structure
2. Add new format handling in `parse_external_api_response()`
3. Check logs for available keys

### Issue: "All forecast values are zero during daytime"

**Cause**: External API returned zeros or parsing failed

**Solution**:
1. Check external API response
2. Verify daytime calculation (IST timezone)
3. Check fallback calculation logs
4. Ensure `is_daytime_by_time` logic is working

### Issue: "Request timeout"

**Cause**: External API taking > 30 seconds

**Solution**:
1. Check external API server status
2. Increase `REQUEST_TIMEOUT` if needed
3. Check network connectivity

### Issue: "Failed to fetch forecast from external API"

**Cause**: HTTP error from external API

**Solution**:
1. Check external API logs
2. Verify API key is correct
3. Check API URL is accessible
4. Verify request format matches API expectations

## Key Design Decisions

1. **Single Source of Truth**: External API is the only source for forecast data
2. **Format Flexibility**: Parser handles multiple response formats
3. **Daytime Validation**: Always ensures daytime values are never zero
4. **Fallback Calculations**: Applies realistic solar curves when data is missing
5. **Error Transparency**: Clear error messages and logging
6. **Timezone Consistency**: All times converted to IST for display
7. **Probabilistic Forecasts**: Uses NGBoost model for uncertainty quantification (P10/P50/P90)
8. **Physics-Based Conversion**: GHI to power conversion uses realistic loss factors
9. **Frontend Transformation**: Hourly forecasts displayed as time-based intervals for better UX

## Data Sources Summary

1. **Weather Data**: Open-Meteo API (ERA5 reanalysis) - used by external API
2. **Forecast Model**: NGBoost (probabilistic gradient boosting) - runs in external API
3. **Power Calculation**: Physics-based conversion with realistic loss factors
4. **Current Values**: Sensor readings (priority) or first forecast point (fallback)

## Summary

The forecast system generates data through:

1. ✅ **NGBoost ML model** trained on 180 days of historical weather
2. ✅ **Probabilistic predictions** (P10/P50/P90) for uncertainty quantification
3. ✅ **Physics-based power conversion** with realistic loss factors (15% system, 5% temp, 5% pollution, 3% soiling)
4. ✅ **Hourly forecasts** displayed as time-based intervals in the UI
5. ✅ **Confidence score** derived from model uncertainty
6. ✅ **Real-time sensor integration** for current values

The data is **real** (not mock) when the external API is working. When it times out, the system falls back to mock data with a warning.

## Future Enhancements

1. **Caching**: Cache external API responses to reduce load
2. **Retry Logic**: Automatic retry on transient failures
3. **Response Validation**: Validate external API response structure
4. **Metrics**: Track API response times and success rates
5. **Fallback API**: Secondary API source if primary fails
6. **Real-time Updates**: WebSocket support for live forecast updates
7. **Historical Analysis**: Compare forecasts with actual performance

## Contact & Support

For issues or questions:
1. Check logs in backend console
2. Review this guide
3. Test external API directly
4. Check database for microgrid configuration

---

**Last Updated**: January 2025
**Version**: 1.0

