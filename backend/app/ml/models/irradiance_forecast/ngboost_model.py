"""
NGBoost probabilistic model for solar irradiance forecasting.
Based on surya_drishti_lite train_ngboost.py
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from pathlib import Path
import joblib
import logging

try:
    from ngboost import NGBRegressor
    from ngboost.distns import Normal
    from ngboost.scores import MLE
    NGBOOST_AVAILABLE = True
except ImportError:
    NGBOOST_AVAILABLE = False
    NGBRegressor = None
    Normal = None
    MLE = None
    logging.warning("NGBoost not installed. Install with: pip install ngboost")

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt

logger = logging.getLogger(__name__)


class NGBoostIrradianceModel:
    """
    NGBoost probabilistic model for 24-hour ahead GHI forecasting.
    Provides both point predictions and uncertainty estimates.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        feature_cols_path: Optional[str] = None,
        n_estimators: int = 500,
        learning_rate: float = 0.05
    ):
        self.model_path = model_path
        self.feature_cols_path = feature_cols_path
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        
        self.model: Optional[NGBRegressor] = None
        self.feature_cols: Optional[List[str]] = None
        
        if not NGBOOST_AVAILABLE:
            raise ImportError("NGBoost is not installed. Install with: pip install ngboost")
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path, feature_cols_path)
    
    def load_model(self, model_path: str, feature_cols_path: Optional[str] = None):
        """Load a trained model from disk"""
        try:
            self.model = joblib.load(model_path)
            logger.info(f"Loaded NGBoost model from {model_path}")
            
            if feature_cols_path and Path(feature_cols_path).exists():
                self.feature_cols = joblib.load(feature_cols_path)
                logger.info(f"Loaded feature columns from {feature_cols_path}")
            elif self.model and hasattr(self.model, 'feature_names_in_'):
                self.feature_cols = list(self.model.feature_names_in_)
                logger.info("Using feature names from model")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "target_24h",
        test_size: float = 0.2,
        save_path: Optional[str] = None,
        feature_cols_path: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Train the NGBoost model on preprocessed data.
        
        Args:
            df: Preprocessed DataFrame with features and target
            target_col: Name of target column
            test_size: Fraction of data to use for testing
            save_path: Path to save trained model
            feature_cols_path: Path to save feature column names
        
        Returns:
            Dictionary with training metrics
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset")
        
        # Separate features and target
        X = df.drop(columns=['time', 'time_local', target_col], errors='ignore')
        y = df[target_col]
        
        # Store feature columns
        self.feature_cols = list(X.columns)
        
        # Split into train/test sets (no shuffling for time-series)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        logger.info(f"Training on {X_train.shape}, testing on {X_test.shape}")
        
        # Initialize and train NGBoost with improved parameters
        self.model = NGBRegressor(
            Dist=Normal,
            Score=MLE,
            verbose=True,
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            minibatch_frac=0.8,  # Use 80% of data for each boosting iteration
            col_sample=0.9,  # Use 90% of features randomly
            early_stopping_rounds=50,  # Stop early if no improvement
            validation_fraction=0.1  # Use 10% for validation
        )
        
        self.model.fit(X_train, y_train)
        
        # Generate predictions and compute metrics
        pred_dist = self.model.pred_dist(X_test)
        y_pred = pred_dist.loc
        
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = sqrt(mse)
        
        # Additional validation metrics
        from sklearn.metrics import r2_score, mean_absolute_percentage_error
        
        r2 = r2_score(y_test, y_pred)
        
        # MAPE (handle division by zero)
        y_test_nonzero = y_test[y_test > 0]
        y_pred_nonzero = y_pred[y_test > 0]
        if len(y_test_nonzero) > 0:
            mape = mean_absolute_percentage_error(y_test_nonzero, y_pred_nonzero)
        else:
            mape = 0.0
        
        # Calculate prediction intervals coverage (for probabilistic model)
        def get_values(obj):
            """Extract values from pandas Series or numpy array"""
            if hasattr(obj, 'values'):
                return obj.values
            elif isinstance(obj, np.ndarray):
                return obj
            else:
                return np.array(obj)
        
        p10_vals = pred_dist.ppf(0.1)
        p90_vals = pred_dist.ppf(0.9)
        p10_array = get_values(p10_vals)
        p90_array = get_values(p90_vals)
        coverage_80 = np.mean((y_test >= p10_array) & (y_test <= p90_array))
        
        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'coverage_80pct': float(coverage_80)
        }
        
        logger.info(f"Training complete - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}, MAPE: {mape:.2f}%, 80% Coverage: {coverage_80:.2%}")
        
        # Save model if path provided
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, save_path)
            logger.info(f"Model saved to {save_path}")
        
        if feature_cols_path:
            Path(feature_cols_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.feature_cols, feature_cols_path)
            logger.info(f"Feature columns saved to {feature_cols_path}")
        
        return metrics
    
    def predict(
        self,
        X: pd.DataFrame,
        return_uncertainty: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Make predictions with uncertainty estimates.
        
        Args:
            X: Feature DataFrame
            return_uncertainty: Whether to return uncertainty estimates
        
        Returns:
            Dictionary with 'mean' (and optionally 'std', 'p10', 'p50', 'p90')
        """
        if self.model is None:
            raise ValueError("Model not loaded or trained")
        
        # Ensure feature columns match
        if self.feature_cols:
            missing_cols = set(self.feature_cols) - set(X.columns)
            if missing_cols:
                logger.warning(f"Missing columns: {missing_cols}, filling with zeros")
                for col in missing_cols:
                    X[col] = 0.0
            X = X[self.feature_cols]
        
        # Get probabilistic predictions
        pred_dist = self.model.pred_dist(X)
        
        # Handle both pandas Series and numpy array cases
        def get_values(obj):
            """Extract values from pandas Series or numpy array"""
            if hasattr(obj, 'values'):
                return obj.values
            elif isinstance(obj, np.ndarray):
                return obj
            else:
                return np.array(obj)
        
        # Get raw predictions
        mean_vals = get_values(pred_dist.loc)
        std_vals = get_values(pred_dist.scale)
        
        # Clip negative values to 0 (irradiance cannot be negative)
        mean_vals = np.maximum(mean_vals, 0.0)
        
        result = {
            'mean': mean_vals,
            'std': std_vals
        }
        
        if return_uncertainty:
            # Calculate quantiles and clip negative values
            p10_vals = get_values(pred_dist.ppf(0.1))
            p50_vals = get_values(pred_dist.loc)  # Median = mean for normal
            p90_vals = get_values(pred_dist.ppf(0.9))
            
            # Clip all quantiles to ensure non-negative
            result['p10'] = np.maximum(p10_vals, 0.0)
            result['p50'] = np.maximum(p50_vals, 0.0)
            result['p90'] = np.maximum(p90_vals, 0.0)
        
        return result
    
    def predict_single(self, X: pd.DataFrame) -> Dict[str, float]:
        """Predict for a single sample, returning a dictionary"""
        results = self.predict(X, return_uncertainty=True)
        return {
            'p10': float(results['p10'][0]),
            'p50': float(results['p50'][0]),
            'p90': float(results['p90'][0]),
            'mean': float(results['mean'][0]),
            'std': float(results['std'][0])
        }


