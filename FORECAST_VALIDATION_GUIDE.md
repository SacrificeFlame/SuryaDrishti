# Forecast Validation Guide

## Overview

The `/api/v1/debug/validate-forecast` endpoint validates solar irradiance and power forecasts to determine if they are realistic, optimistic, or incorrect.

## Usage

### Endpoint
```
POST /api/v1/debug/validate-forecast
```

### Request Body
Send the forecast response from either:
- `/api/v1/forecast/microgrid/{id}`
- `/api/v1/forecast/ngboost`

### Example Request

```bash
# Get a forecast
curl http://localhost:8000/api/v1/forecast/microgrid/mg_001 > forecast.json

# Validate it
curl -X POST http://localhost:8000/api/v1/debug/validate-forecast \
  -H "Content-Type: application/json" \
  -d @forecast.json
```

### Example Response

```json
{
  "status": "ok",
  "verdict": "optimistic",
  "severity": "medium",
  "summary": {
    "total_points": 24,
    "daytime_points": 12,
    "max_ghi_w_m2": 850.0,
    "mean_ghi_w_m2": 216.0,
    "max_power_kw": 40.5,
    "mean_power_kw": 10.3,
    "peak_capacity_factor_percent": 81.0,
    "avg_clear_sky_ratio": 1.15
  },
  "checks": {
    "passed": [
      "Peak GHI (850.0 W/m²) is within reasonable range"
    ],
    "warnings": [
      "Peak capacity factor (81.0%) is high - verify site conditions",
      "Average clear-sky ratio (1.15) indicates overly optimistic forecasts"
    ],
    "issues": []
  },
  "possible_causes": [
    "Loss factors (temperature, pollution, soiling) may be underestimated",
    "Forecast exceeds clear-sky model - check for data leakage or model calibration issues"
  ],
  "recommendations": [
    "Compare with historical data for the same location and time",
    "Verify clear-sky GHI calculations using pvlib",
    "Check if loss factors match local conditions (pollution, temperature, soiling)"
  ]
}
```

## Validation Checks

### 1. Peak GHI Values
- **Issue**: > 1000 W/m² (exceeds physical maximum)
- **Warning**: > 900 W/m² (very high, verify clear-sky)
- **Pass**: 0-900 W/m² (reasonable range)

### 2. Capacity Factor
- **Issue**: Peak > 85% (unrealistically high)
- **Warning**: Peak > 75% (high, verify site conditions)
- **Warning**: Average > 40% (high for horizontal panels)
- **Pass**: Realistic ranges (peak 60-75%, average 25-35%)

### 3. Clear-Sky Comparison
- **Issue**: Ratio > 1.15 (exceeds clear-sky by >15%)
- **Warning**: Ratio > 1.10 (exceeds clear-sky by >10%)
- **Warning**: Ratio < 0.3 (very low, heavy cloud cover)
- **Pass**: Ratio 0.3-1.10 (reasonable)

### 4. Solar Elevation vs GHI
- Checks if GHI at maximum solar elevation exceeds expected values
- Expected GHI scales with sin(elevation)
- Flags if actual > expected × 1.2

### 5. Daytime Detection
- Verifies that daytime hours (6 AM - 7 PM) are correctly identified
- Flags if points that should be daytime are marked as nighttime

### 6. Power Conversion Consistency
- Validates power conversion efficiency (~77% expected)
- Checks if actual efficiency differs from expected by >15%

## Verdicts

### "realistic"
- No issues or warnings
- All checks passed
- Forecast values are physically reasonable

### "mostly realistic"
- 1 warning (minor concern)
- Most checks passed
- Forecast is generally good with minor caveats

### "optimistic"
- 2+ warnings
- Forecast may be overestimating values
- Still physically possible but may not reflect real-world conditions

### "incorrect"
- 1+ issues (serious problems)
- Forecast violates physical constraints
- Values are not physically possible

## Expected Values for Delhi/India

### GHI (Global Horizontal Irradiance)
- **Peak**: 800-1000 W/m² (clear sky, midday)
- **Typical midday**: 600-800 W/m²
- **Daily average**: ~208 W/m² (5 kWh/m²/day ÷ 24h)

### Capacity Factor (50 kW System)
- **Peak**: 60-76% (30-38 kW)
- **Average**: 25-35% (12.5-17.5 kW)
- **Annual**: ~20-25%

### Clear-Sky Ratio
- **Clear sky**: 0.9-1.0
- **Partly cloudy**: 0.5-0.9
- **Heavy clouds**: 0.2-0.5
- **Very cloudy**: < 0.2

## Possible Causes

The endpoint identifies common causes for unrealistic forecasts:

1. **Model overestimating clear-sky conditions**
   - Solution: Review model training data, check for data leakage

2. **Loss factors underestimated**
   - Solution: Adjust temperature, pollution, soiling factors for local conditions

3. **Forecast exceeds clear-sky model**
   - Solution: Check model calibration, verify clear-sky calculations

4. **Daytime detection issues**
   - Solution: Review solar elevation calculations, timezone handling

## Recommendations

The endpoint provides specific recommendations based on detected issues:

- Compare with historical data
- Verify clear-sky GHI calculations
- Check loss factors match local conditions
- Validate solar elevation calculations
- Review model training data for data leakage

## Integration Example

```python
import requests

# Get forecast
forecast_response = requests.get(
    "http://localhost:8000/api/v1/forecast/microgrid/mg_001"
)
forecast_data = forecast_response.json()

# Validate forecast
validation_response = requests.post(
    "http://localhost:8000/api/v1/debug/validate-forecast",
    json=forecast_data
)
validation = validation_response.json()

# Check verdict
if validation["verdict"] == "realistic":
    print("✅ Forecast is realistic")
elif validation["verdict"] == "optimistic":
    print("⚠️ Forecast may be optimistic")
    print("Possible causes:", validation["possible_causes"])
else:
    print("❌ Forecast has issues")
    print("Issues:", validation["checks"]["issues"])
```

## Notes

- The validation compares forecasts against physical constraints and typical values
- It does NOT compare with actual measurements (use historical data for that)
- Results are location-agnostic but calibrated for Delhi/India conditions
- Adjust thresholds for different locations/climates
