"""
Internal /api/run endpoint for forecast generation.
This endpoint is called by external_forecast_service to generate forecasts.
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Body
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import logging
import pandas as pd
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

# API Key validation
EXTERNAL_API_KEY = "aryan1234%^&*()"


@router.post("/api/run")
async def run_forecast(
    request_data: Dict = Body(...),
    x_api_key: Optional[str] = Header(None, alias="x-api-key"),
    db: Session = Depends(get_db)
):
    """
    Internal forecast generation endpoint.
    Called by external_forecast_service to generate forecasts.
    
    Request Body:
    {
        "source": "hybrid" | "ngboost" | "open-meteo"
    }
    
    Headers:
    - x-api-key: API key for authentication
    """
    try:
        # Validate API key
        if x_api_key != EXTERNAL_API_KEY:
            logger.warning(f"Invalid API key provided")
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        # Get source from request
        source = request_data.get("source", "hybrid")
        logger.info(f"Generating forecast with source: {source}")
        
        # Default location (Delhi/NCR)
        lat = 28.4595
        lon = 77.0266
        horizon_hours = 24
        training_days = request_data.get("training_days", 90)  # Reduced default to 90 days for faster training
        
        # Use the existing NGBoost forecast endpoint logic
        from app.services.open_meteo_service import OpenMeteoService
        from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data
        from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel
        import numpy as np
        from pathlib import Path
        
        logger.info(f"Fetching NGBoost forecast for ({lat}, {lon}), horizon={horizon_hours}h")
        
        # Initialize services
        meteo_service = OpenMeteoService()
        
        # Fetch data
        logger.info("Fetching Open-Meteo data...")
        hist_df, fc_df = meteo_service.fetch_combined(
            lat=lat,
            lon=lon,
            past_days=training_days,
            forecast_hours=horizon_hours
        )
        
        if hist_df.empty or fc_df.empty:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch weather data"
            )
        
        # Preprocess data
        logger.info("Preprocessing data...")
        df_processed = preprocess_open_meteo_data(
            hist_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=horizon_hours
        )
        
        # Load or train model
        model_path = Path("data/models/ngboost_24h.joblib")
        feature_path = Path("data/models/ngboost_features.joblib")
        
        # Ensure model directory exists
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        retrain = request_data.get("retrain", False)
        if retrain or not model_path.exists():
            logger.info("Training NGBoost model...")
            model = NGBoostIrradianceModel()
            target_col = f"target_{horizon_hours}h"
            # Use smaller dataset for faster training if model doesn't exist
            if not model_path.exists() and len(df_processed) > 1000:
                logger.info(f"Using subset of data for faster initial training: {len(df_processed)} -> 1000 rows")
                df_train = df_processed.sample(n=min(1000, len(df_processed)), random_state=42)
            else:
                df_train = df_processed
            model.train(
                df_train,
                target_col=target_col,
                save_path=str(model_path),
                feature_cols_path=str(feature_path)
            )
        else:
            logger.info("Loading existing NGBoost model...")
            model = NGBoostIrradianceModel()
            model.load_model(str(model_path), feature_cols_path=str(feature_path) if feature_path.exists() else None)
        
        # Preprocess forecast data for prediction
        fc_processed = preprocess_open_meteo_data(
            fc_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=0  # No target for forecast
        )
        
        # Make predictions
        logger.info("Generating predictions...")
        predictions = model.predict(fc_processed, return_uncertainty=True)
        
        # Format response
        # Get time column (try time_local first, then time)
        time_col = "time_local" if "time_local" in fc_processed.columns else "time"
        forecast_times = fc_processed[time_col].dt.strftime("%Y-%m-%d %H:%M").tolist()
        
        forecast_data = []
        for i, time_str in enumerate(forecast_times):
            # Get timestamp - use time column or convert from time_local
            if time_col == "time_local":
                timestamp = fc_processed[time_col].iloc[i]
                if hasattr(timestamp, 'isoformat'):
                    timestamp_str = timestamp.isoformat()
                else:
                    timestamp_str = pd.Timestamp(timestamp).isoformat()
            else:
                timestamp_str = fc_processed["time"].iloc[i].isoformat()
            
            forecast_item = {
                "time": time_str,
                "timestamp": timestamp_str,
                "p10": float(predictions["p10"][i]),
                "p50": float(predictions["p50"][i]),
                "p90": float(predictions["p90"][i]),
                "mean": float(predictions["mean"][i]),
                "std": float(predictions["std"][i]),
                "ghi": float(predictions["mean"][i])
            }
            forecast_data.append(forecast_item)
        
        # Return in format expected by external_forecast_service
        result = {
            "status": "ok",
            "model": "ngboost",
            "location": {"lat": lat, "lon": lon},
            "horizon_hours": horizon_hours,
            "forecast": forecast_data,
            "summary": {
                "mean_ghi": float(np.mean([f["ghi"] for f in forecast_data])),
                "max_ghi": float(np.max([f["ghi"] for f in forecast_data])),
                "min_ghi": float(np.min([f["ghi"] for f in forecast_data])),
                "avg_uncertainty": float(np.mean([f["std"] for f in forecast_data]))
            },
            "metadata": {
                "data_source": "open-meteo",
                "retrained": False,
                "training_days": training_days,
                "n_samples": len(forecast_data),
                "features_used": len(fc_processed.columns) - 1
            }
        }
        
        logger.info(f"Successfully generated forecast: {len(forecast_data)} points")
        
        return JSONResponse(
            content=result,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /api/run endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Forecast generation failed: {str(e)[:200]}"
        )

