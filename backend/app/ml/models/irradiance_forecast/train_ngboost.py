"""
Training script for NGBoost irradiance forecasting model.
Based on surya_drishti_lite train_ngboost.py
"""
import sysgive
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.services.open_meteo_service import OpenMeteoService
from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data
from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel
from app.core.config import settings
import logging
import argparse
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_ngboost_model(
    lat: float,
    lon: float,
    past_days: int = 365,
    target_horizon_hours: int = 24,
    model_save_path: Optional[str] = None,
    feature_cols_path: Optional[str] = None
):
    """
    Train NGBoost model for a specific location.
    
    Args:
        lat: Latitude
        lon: Longitude
        past_days: Number of days of historical data to fetch
        target_horizon_hours: Hours ahead to predict
        model_save_path: Path to save trained model
        feature_cols_path: Path to save feature columns
    """
    logger.info(f"Training NGBoost model for location ({lat}, {lon})")
    
    # Fetch data
    meteo_service = OpenMeteoService()
    logger.info(f"Fetching {past_days} days of historical data...")
    hist_df, _ = meteo_service.fetch_combined(lat, lon, past_days=past_days)
    
    # Preprocess data
    logger.info("Preprocessing data...")
    df_processed = preprocess_open_meteo_data(
        hist_df,
        lat=lat,
        lon=lon,
        target_horizon_hours=target_horizon_hours
    )
    
    # Train model
    target_col = f"target_{target_horizon_hours}h"
    model = NGBoostIrradianceModel()
    
    logger.info("Training model...")
    metrics = model.train(
        df_processed,
        target_col=target_col,
        save_path=model_save_path,
        feature_cols_path=feature_cols_path
    )
    
    logger.info(f"Training complete! Metrics: {metrics}")
    return model, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train NGBoost irradiance forecasting model")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--days", type=int, default=365, help="Days of historical data")
    parser.add_argument("--horizon", type=int, default=24, help="Forecast horizon in hours")
    parser.add_argument("--model-path", type=str, default="data/models/ngboost_24h.joblib",
                       help="Path to save model")
    parser.add_argument("--features-path", type=str, default="data/models/ngboost_features.joblib",
                       help="Path to save feature columns")
    
    args = parser.parse_args()
    
    train_ngboost_model(
        lat=args.lat,
        lon=args.lon,
        past_days=args.days,
        target_horizon_hours=args.horizon,
        model_save_path=args.model_path,
        feature_cols_path=args.features_path
    )

