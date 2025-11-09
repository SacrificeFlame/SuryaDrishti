# SuryaDrishti Lite Integration

This document describes the integration of components from the [surya_drishti_lite](https://github.com/SkillzIsStupid/surya_drishti_lite) repository into the main SuryaDrishti project.

## Overview

The `surya_drishti_lite` repository provides a lightweight prototype for solar irradiance forecasting using:
- **Open-Meteo API** for weather data (instead of satellite imagery)
- **NGBoost** probabilistic model for 24-hour ahead GHI forecasting
- **pvlib** for solar geometry and clear-sky calculations

## Integrated Components

### 1. Open-Meteo Service (`backend/app/services/open_meteo_service.py`)

Service for fetching historical and forecast weather data from Open-Meteo API.

**Features:**
- Fetch historical data from ERA5 archive
- Fetch forecast data for next 24-48 hours
- Supports custom timezones (default: Asia/Kolkata)

**Usage:**
```python
from app.services.open_meteo_service import OpenMeteoService

service = OpenMeteoService()
hist_df, fc_df = service.fetch_combined(lat=28.7, lon=77.1, past_days=365)
```

### 2. Data Preprocessing (`backend/app/ml/preprocessing/open_meteo_preprocess.py`)

Preprocessing pipeline for Open-Meteo data using pvlib.

**Features:**
- Robust timezone handling
- Solar geometry calculations (elevation, zenith, azimuth)
- Clear-sky GHI computation using Ineichen model
- Feature engineering (time features, lag features, trends)
- Data leakage prevention (1-hour shift for radiation data)

**Usage:**
```python
from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data

df_processed = preprocess_open_meteo_data(df, lat=28.7, lon=77.1, target_horizon_hours=24)
```

### 3. NGBoost Model (`backend/app/ml/models/irradiance_forecast/ngboost_model.py`)

Probabilistic forecasting model using NGBoost.

**Features:**
- Probabilistic predictions (P10, P50, P90 quantiles)
- Uncertainty estimates (mean, std)
- Model persistence (save/load)
- Automatic feature column management

**Usage:**
```python
from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel

# Train
model = NGBoostIrradianceModel()
metrics = model.train(df, target_col="target_24h", save_path="models/ngboost.joblib")

# Predict
predictions = model.predict(X, return_uncertainty=True)
# Returns: {'mean', 'std', 'p10', 'p50', 'p90'}
```

### 4. Training Script (`backend/app/ml/models/irradiance_forecast/train_ngboost.py`)

Standalone script for training NGBoost models.

**Usage:**
```bash
python -m app.ml.models.irradiance_forecast.train_ngboost \
    --lat 28.7041 \
    --lon 77.1025 \
    --days 365 \
    --horizon 24 \
    --model-path data/models/ngboost_24h.joblib
```

### 5. API Endpoint (`backend/app/api/v1/forecast.py`)

New endpoint `/api/v1/forecast/ngboost` for NGBoost-based forecasting.

**Endpoint:** `GET /api/v1/forecast/ngboost`

**Parameters:**
- `lat` (required): Latitude
- `lon` (required): Longitude
- `horizon_hours` (optional, default=24): Forecast horizon in hours
- `retrain` (optional, default=false): Retrain model on fresh data

**Response:**
```json
{
  "status": "ok",
  "model": "ngboost",
  "location": {"lat": 28.7, "lon": 77.1},
  "horizon_hours": 24,
  "forecast": [
    {
      "time": "2025-01-15 10:00",
      "timestamp": "2025-01-15T10:00:00+05:30",
      "p10": 450.2,
      "p50": 650.8,
      "p90": 850.3,
      "mean": 650.8,
      "std": 120.5,
      "ghi": 650.8
    },
    ...
  ],
  "metadata": {
    "data_source": "open-meteo",
    "retrained": false,
    "n_samples": 24
  }
}
```

## Dependencies Added

The following packages were added to `requirements.txt`:
- `ngboost==0.4.2` - Probabilistic gradient boosting
- `pvlib==0.10.3` - Solar energy modeling
- `python-dateutil==2.8.2` - Date parsing utilities
- `pytz==2024.1` - Timezone support

## Installation

Install the new dependencies:
```bash
pip install -r backend/requirements.txt
```

## Usage Examples

### 1. Train a Model
```python
from app.services.open_meteo_service import OpenMeteoService
from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data
from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel

# Fetch data
service = OpenMeteoService()
hist_df, _ = service.fetch_combined(28.7, 77.1, past_days=365)

# Preprocess
df = preprocess_open_meteo_data(hist_df, 28.7, 77.1, target_horizon_hours=24)

# Train
model = NGBoostIrradianceModel()
metrics = model.train(df, save_path="data/models/ngboost_24h.joblib")
```

### 2. Make Predictions
```python
from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel

model = NGBoostIrradianceModel(
    model_path="data/models/ngboost_24h.joblib",
    feature_cols_path="data/models/ngboost_features.joblib"
)

predictions = model.predict(X, return_uncertainty=True)
```

### 3. Use API Endpoint
```bash
curl "http://localhost:8000/api/v1/forecast/ngboost?lat=28.7&lon=77.1&horizon_hours=24"
```

## Differences from Original surya_drishti_lite

1. **Framework**: Adapted from Flask to FastAPI
2. **Integration**: Integrated into existing service architecture
3. **Async Support**: Open-Meteo service supports async operations
4. **Error Handling**: Enhanced error handling and logging
5. **Type Hints**: Added type hints throughout
6. **Configuration**: Uses existing config system

## Notes

- The NGBoost model provides probabilistic forecasts, which is useful for uncertainty quantification
- Open-Meteo is free and doesn't require API keys, making it ideal for prototyping
- For production, consider using MOSDAC data (as mentioned in original repo) for better accuracy
- The model retrains on each request if `retrain=true`, which can be slow. In production, train periodically and serve from cache.

## References

- Original repository: https://github.com/SkillzIsStupid/surya_drishti_lite
- Open-Meteo API: https://open-meteo.com/
- NGBoost: https://stanfordmlgroup.github.io/ngboost/
- pvlib: https://pvlib-python.readthedocs.io/



