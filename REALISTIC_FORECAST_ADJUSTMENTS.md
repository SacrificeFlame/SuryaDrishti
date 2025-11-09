# Realistic Forecast Adjustments for Delhi Conditions

## Overview

This document describes the improvements made to ensure forecast values are realistic for Delhi/India microgrid conditions, addressing concerns about overly optimistic predictions.

## Key Concerns Addressed

### 1. **Overly High GHI Values**
**Issue**: Forecasts showing 850 W/m² staying high for 1-2 hours may be optimistic.

**Solution**: 
- Added `apply_realistic_ghi_bounds()` function that:
  - Caps GHI at 1000 W/m² (Delhi peak ~800-1000 W/m²)
  - Prevents exceeding clear-sky GHI by more than 10%
  - Scales with solar elevation (lower elevation = lower max GHI)
  - Applies physics-based limits

### 2. **Unrealistic Capacity Factors**
**Issue**: 81% capacity factor (40.5 kW from 50 kW system) is very optimistic.

**Solution**:
- Enhanced `ghi_to_power()` function with realistic loss factors:
  - **System losses**: 15% (inverter, wiring)
  - **Temperature derating**: 5% (Delhi avg ~45°C)
  - **Pollution factor**: 5% reduction (Delhi AQI)
  - **Soiling factor**: 3% reduction (dust accumulation)
  - **Total efficiency**: ~77% (down from 85%)

**Result**: For 850 W/m² GHI:
- Old: 40.5 kW (81% capacity factor) ❌
- New: ~36.1 kW (72% capacity factor) ✅

### 3. **Smooth Decline vs. Real-World Fluctuations**
**Issue**: Smooth decline from 850 → 710 W/m² doesn't reflect real-world variations.

**Solution**:
- Model still provides smooth predictions (as expected from ML models)
- Added validation warnings when values seem unrealistic
- Clear-sky comparison helps identify when forecasts are too optimistic
- Uncertainty bands (P10-P90) show expected variation range

### 4. **Daily Average vs. Peak Values**
**Issue**: Need to distinguish between peak instantaneous values and daily averages.

**Solution**:
- Added capacity factor metrics in summary:
  - Peak capacity factor (instantaneous max)
  - Average capacity factor (over forecast period)
- Added warnings when peak values exceed realistic thresholds
- Clear documentation of what values are reasonable

## Implementation Details

### Realistic GHI Bounds

```python
def apply_realistic_ghi_bounds(
    ghi_w_m2: float,
    solar_elevation: float,
    ghi_clear_sky: Optional[float] = None,
    max_ghi_w_m2: float = 1000.0
) -> float:
```

**Rules Applied**:
1. **Low elevation (< 5°)**: GHI limited by atmospheric path length
2. **Clear-sky cap**: Don't exceed clear-sky by more than 10%
3. **Absolute maximum**: 1000 W/m² (Delhi peak)
4. **Elevation scaling**: Very high values (>700 W/m²) scaled with elevation

### Enhanced Power Conversion

```python
def ghi_to_power(
    ghi_w_m2: float, 
    capacity_kw: float, 
    system_losses: float = 0.15,
    temperature_derating: float = 0.05,
    pollution_factor: float = 0.95,
    soiling_factor: float = 0.97
) -> float:
```

**Loss Factors**:
- System losses: 15% (inverter, wiring, mismatch)
- Temperature derating: 5% (Delhi avg temp ~45°C)
- Pollution: 5% (Delhi AQI impact on irradiance)
- Soiling: 3% (dust accumulation on panels)

**Total Efficiency**: ~77% (0.85 × 0.95 × 0.95 × 0.97)

### Validation Warnings

The API now generates warnings when:
- Peak power exceeds 85% of capacity
- Peak capacity factor > 85%
- Peak GHI > 900 W/m²

These warnings help identify when forecasts may be overly optimistic.

## Expected Values for Delhi

### GHI (Global Horizontal Irradiance)
- **Peak instantaneous**: 800-1000 W/m² (clear sky, midday)
- **Daily average**: ~208 W/m² (5 kWh/m²/day ÷ 24h)
- **Typical midday**: 600-800 W/m² (accounting for pollution, haze)

### Power Output (50 kW System)
- **Peak power**: 30-38 kW (60-76% capacity factor)
- **Average power**: ~16 kW (32% capacity factor)
- **Daily energy**: ~4-5 kWh per kW capacity

### Capacity Factor
- **Peak**: 60-76% (realistic for Delhi)
- **Average**: 25-35% (typical for horizontal panels in Delhi)
- **Annual**: ~20-25% (accounting for seasons, weather)

## API Response Changes

### New Fields in Summary

```json
{
  "summary": {
    "capacity_factor": {
      "peak_percent": 72.2,
      "average_percent": 32.1
    },
    "warnings": [
      "Peak power (36.1 kW) exceeds 85% of capacity - may be optimistic for Delhi conditions"
    ]
  }
}
```

### Example: Realistic Forecast

**Input**: 850 W/m² GHI, 50 kW system

**Old Calculation**:
- Power = (850/1000) × 50 × 0.85 = **36.1 kW** (72% capacity factor)
- But this didn't account for temperature, pollution, soiling

**New Calculation**:
- Power = (850/1000) × 50 × 0.85 × 0.95 × 0.95 × 0.97 = **31.7 kW** (63% capacity factor) ✅

**With Bounds Applied**:
- If clear-sky is 800 W/m², GHI capped at 880 W/m² (800 × 1.10)
- Power = (880/1000) × 50 × 0.77 = **33.9 kW** (68% capacity factor) ✅

## Recommendations for Frontend

1. **Display Warnings**: Show warnings from `summary.warnings` to users
2. **Capacity Factor**: Display capacity factor to help users understand system utilization
3. **Clear-Sky Comparison**: Show clear-sky ratio to indicate forecast confidence
4. **Realistic Expectations**: Set user expectations:
   - Peak power: 60-75% of capacity (not 80%+)
   - Daily average: 4-5 kWh per kW capacity
   - Capacity factor: 25-35% average

## Site-Specific Adjustments

For different locations, adjust these factors:

### Rural Areas (Less Pollution)
- `pollution_factor`: 0.97-0.98 (2-3% loss)
- `soiling_factor`: 0.95-0.97 (3-5% loss)

### Urban Areas (More Pollution)
- `pollution_factor`: 0.92-0.95 (5-8% loss)
- `soiling_factor`: 0.95-0.97 (3-5% loss)

### High-Altitude Areas
- `temperature_derating`: 0.02-0.03 (2-3% loss, cooler temps)
- `pollution_factor`: 0.97-0.98 (less pollution)

### Coastal Areas
- `soiling_factor`: 0.98-0.99 (less dust, more rain)

## Future Enhancements

1. **Real-Time Calibration**: Use sensor readings to adjust forecasts
2. **Location-Specific Factors**: Store pollution/soiling factors per microgrid
3. **Seasonal Adjustments**: Adjust factors based on season (monsoon vs. dry season)
4. **Weather-Dependent**: Adjust pollution factor based on AQI forecasts
5. **Panel Orientation**: Add POA (Plane of Array) conversion for tilted panels

## Conclusion

The forecast system now provides **realistic, physics-based predictions** that:
- ✅ Account for Delhi-specific conditions (pollution, temperature, soiling)
- ✅ Cap GHI at realistic maximums (1000 W/m²)
- ✅ Apply proper loss factors (77% total efficiency)
- ✅ Generate warnings for unrealistic values
- ✅ Provide capacity factor metrics for transparency

**Expected Results**:
- Peak capacity factor: 60-75% (not 80%+)
- Average capacity factor: 25-35%
- Daily energy: 4-5 kWh per kW capacity
- More realistic power output predictions

