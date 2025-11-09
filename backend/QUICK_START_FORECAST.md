# Quick Start: Forecast & Scheduler

## TL;DR

The forecast and scheduler now use the external API at `http://127.0.0.1:8000/api/run` with `{"source": "hybrid"}`.

## Key Endpoints

### 1. Dashboard Forecast
```
GET /api/v1/forecast/microgrid/microgrid_001?horizon_hours=24
```
Returns forecast data for the main dashboard.

### 2. Forecast Schedule
```
POST /api/v1/forecast/schedule?forecast_hours=12
```
Returns forecast data in schedule format for the forecast-schedule page.

### 3. Generate Schedule
```
POST /api/v1/microgrid/microgrid_001/schedules/generate
Body: {"use_forecast": true}
```
Generates optimized energy schedule using forecast data.

## How It Works

1. **External API Call**: `POST http://127.0.0.1:8000/api/run` with `{"source": "hybrid"}`
2. **Parse Response**: Handles multiple response formats automatically
3. **Convert Format**: Converts to internal format expected by frontend
4. **Daytime Validation**: Ensures daytime values are never zero
5. **Return Data**: Returns in format expected by dashboard/scheduler

## Configuration

**File**: `backend/app/services/external_forecast_service.py`

```python
EXTERNAL_API_URL = "http://127.0.0.1:8000/api/run"
EXTERNAL_API_KEY = "aryan1234%^&*()"
REQUEST_TIMEOUT = 30.0  # seconds
```

## Testing

```bash
# Test external API
curl -X POST "http://127.0.0.1:8000/api/run" \
  -H "x-api-key: aryan1234%^&*()" \
  -H "Content-Type: application/json" \
  -d '{"source":"hybrid"}'

# Test forecast endpoint
curl "http://localhost:8000/api/v1/forecast/microgrid/microgrid_001?horizon_hours=12"
```

## Important Notes

- **Daytime**: 6:00 AM to 7:00 PM IST - values should never be zero
- **Nighttime**: All values are set to zero (physics: no sun = no power)
- **Fallback**: If daytime values are zero, system applies realistic solar curve
- **Timezone**: All times are converted to IST for display

## Troubleshooting

- **All zeros during daytime**: Check external API response, verify IST timezone calculation
- **Timeout errors**: Check external API server, increase timeout if needed
- **Format errors**: Check external API response structure, update parser if needed

See `FORECAST_SCHEDULER_GUIDE.md` for detailed documentation.

