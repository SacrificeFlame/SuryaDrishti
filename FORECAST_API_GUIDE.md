# Solar Irradiance Forecast API - Complete Guide

## 🚀 Available Endpoints

### 1. **NGBoost Forecast** (Enhanced)
**Endpoint**: `GET /api/v1/forecast/ngboost`

**Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude  
- `horizon_hours` (optional, default=24): Forecast horizon (1-48 hours)
- `training_days` (optional, default=180): Days of historical data (30-730)
- `retrain` (optional, default=false): Force retrain model

**Example:**
```bash
curl "http://localhost:8000/api/v1/forecast/ngboost?lat=28.7&lon=77.1&training_days=365"
```

**Response includes:**
- Probabilistic forecasts (P10, P50, P90 quantiles)
- Uncertainty estimates (mean, std)
- Clear-sky comparison (ghi_clear_sky, clear_sky_ratio)
- Solar elevation
- Summary statistics

### 2. **Hybrid Forecast** (Best Accuracy) ⭐
**Endpoint**: `GET /api/v1/forecast/hybrid`

**Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude
- `horizon_hours` (optional, default=24): Forecast horizon (1-48 hours)
- `use_satellite` (optional, default=true): Include satellite cloud data
- `training_days` (optional, default=180): Days of historical data

**Example:**
```bash
curl "http://localhost:8000/api/v1/forecast/hybrid?lat=28.7&lon=77.1&use_satellite=true"
```

**Response includes:**
- All features from NGBoost endpoint
- Satellite data status and features
- Model training metrics (MAE, RMSE, R², MAPE, coverage)
- Combined data sources

## 📊 Response Format

```json
{
  "status": "ok",
  "model": "ngboost" | "hybrid_ngboost",
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
  "metadata": {
    "data_source": "open-meteo",
    "training_days": 180,
    "n_samples": 24,
    "features_used": 35
  }
}
```

## 🎯 When to Use Which Endpoint

### Use **NGBoost** (`/ngboost`) when:
- ✅ You need fast forecasts
- ✅ Satellite data is not available
- ✅ You want to use a pre-trained model
- ✅ General purpose forecasting

### Use **Hybrid** (`/hybrid`) when:
- ✅ You need maximum accuracy
- ✅ Satellite data is available
- ✅ You want real-time cloud observations
- ✅ Production-critical applications

## ⚙️ Performance Tips

1. **Training Data**: More is better
   - `training_days=365`: Best accuracy, slower training
   - `training_days=180`: Good balance (default)
   - `training_days=90`: Faster, less accurate

2. **Retraining**: 
   - Set `retrain=true` periodically (weekly/monthly)
   - First request with new location will train automatically

3. **Satellite Data**:
   - Hybrid endpoint automatically falls back if satellite unavailable
   - Set `use_satellite=false` to skip satellite fetch (faster)

## 📈 Expected Accuracy

- **NGBoost (180 days)**: RMSE ~40-60 W/m²
- **Hybrid (180 days)**: RMSE ~30-50 W/m²
- **NGBoost (365 days)**: RMSE ~35-55 W/m²
- **Hybrid (365 days)**: RMSE ~25-45 W/m²

## 🔍 Understanding the Forecast

- **P10**: 10% chance actual will be below this (conservative)
- **P50**: Median forecast (most likely)
- **P90**: 10% chance actual will be above this (optimistic)
- **Clear-sky ratio**: Actual/clear-sky (1.0 = clear, <0.5 = cloudy)

## 🛠️ Troubleshooting

**Slow responses?**
- Reduce `training_days` parameter
- Use pre-trained model (don't set `retrain=true`)
- Set `use_satellite=false` for hybrid endpoint

**Low accuracy?**
- Increase `training_days` to 365
- Use hybrid endpoint with satellite data
- Retrain model with `retrain=true`

**Negative values?**
- Fixed automatically (clipped to 0)
- If you see negative P10, model uncertainty is high






