"""
Model calibration utilities for improving forecast accuracy.
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def calibrate_predictions(
    predictions: np.ndarray,
    observed: np.ndarray,
    method: str = "linear"
) -> Tuple[np.ndarray, Dict]:
    """
    Calibrate predictions based on observed values.
    
    Args:
        predictions: Model predictions
        observed: Observed/actual values
        method: Calibration method ('linear', 'quantile', 'isotonic')
    
    Returns:
        Calibrated predictions and calibration parameters
    """
    predictions = np.array(predictions)
    observed = np.array(observed)
    
    # Remove invalid values
    valid_mask = (predictions >= 0) & (observed >= 0) & np.isfinite(predictions) & np.isfinite(observed)
    pred_valid = predictions[valid_mask]
    obs_valid = observed[valid_mask]
    
    if len(pred_valid) == 0:
        logger.warning("No valid data for calibration, returning original predictions")
        return predictions, {}
    
    if method == "linear":
        # Simple linear regression calibration
        from sklearn.linear_model import LinearRegression
        reg = LinearRegression()
        reg.fit(pred_valid.reshape(-1, 1), obs_valid)
        
        calibrated = reg.predict(predictions.reshape(-1, 1))
        calibrated = np.maximum(calibrated, 0)  # Clip negative values
        
        params = {
            "slope": float(reg.coef_[0]),
            "intercept": float(reg.intercept_),
            "r2": float(reg.score(pred_valid.reshape(-1, 1), obs_valid))
        }
        
        logger.info(f"Linear calibration: slope={params['slope']:.3f}, intercept={params['intercept']:.3f}, R²={params['r2']:.3f}")
        return calibrated, params
    
    elif method == "quantile":
        # Quantile mapping calibration
        from scipy import stats
        
        # Map prediction quantiles to observed quantiles
        pred_sorted = np.sort(pred_valid)
        obs_sorted = np.sort(obs_valid)
        
        # Interpolate
        calibrated = np.interp(predictions, pred_sorted, obs_sorted)
        calibrated = np.maximum(calibrated, 0)
        
        params = {"method": "quantile", "n_samples": len(pred_valid)}
        return calibrated, params
    
    else:
        logger.warning(f"Unknown calibration method: {method}, returning original")
        return predictions, {}


def validate_forecast(
    predictions: Dict[str, np.ndarray],
    observed: Optional[np.ndarray] = None
) -> Dict:
    """
    Validate forecast quality.
    
    Args:
        predictions: Dictionary with 'mean', 'p10', 'p50', 'p90', 'std'
        observed: Optional observed values for validation
    
    Returns:
        Validation metrics
    """
    metrics = {}
    
    mean_pred = predictions.get('mean', predictions.get('p50', np.array([])))
    
    # Basic statistics
    metrics['mean_prediction'] = float(np.mean(mean_pred))
    metrics['std_prediction'] = float(np.std(mean_pred))
    metrics['min_prediction'] = float(np.min(mean_pred))
    metrics['max_prediction'] = float(np.max(mean_pred))
    
    # Uncertainty metrics
    if 'std' in predictions:
        metrics['avg_uncertainty'] = float(np.mean(predictions['std']))
        metrics['uncertainty_ratio'] = float(np.mean(predictions['std']) / (np.mean(mean_pred) + 1e-9))
    
    # Prediction interval width
    if 'p10' in predictions and 'p90' in predictions:
        interval_width = predictions['p90'] - predictions['p10']
        metrics['avg_interval_width'] = float(np.mean(interval_width))
        metrics['interval_width_ratio'] = float(np.mean(interval_width) / (np.mean(mean_pred) + 1e-9))
    
    # Validation against observed (if available)
    if observed is not None:
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from math import sqrt
        
        obs_array = np.array(observed)
        valid_mask = (mean_pred > 0) & (obs_array > 0) & np.isfinite(mean_pred) & np.isfinite(obs_array)
        
        if np.sum(valid_mask) > 0:
            pred_valid = mean_pred[valid_mask]
            obs_valid = obs_array[valid_mask]
            
            metrics['mae'] = float(mean_absolute_error(obs_valid, pred_valid))
            metrics['rmse'] = float(sqrt(mean_squared_error(obs_valid, pred_valid)))
            metrics['r2'] = float(r2_score(obs_valid, pred_valid))
            
            # Coverage of prediction intervals
            if 'p10' in predictions and 'p90' in predictions:
                p10_valid = predictions['p10'][valid_mask]
                p90_valid = predictions['p90'][valid_mask]
                coverage = np.mean((obs_valid >= p10_valid) & (obs_valid <= p90_valid))
                metrics['coverage_80pct'] = float(coverage)
    
    return metrics






