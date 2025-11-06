import numpy as np
import torch
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.ml.models.cloud_segmentation.unet import CloudSegmentationInference
from app.ml.models.motion_estimation.optical_flow import CloudMotionTracker
from app.ml.models.irradiance_forecast.pinn import IrradianceInference
from app.services.satellite_ingest import SatelliteDataIngester
from app.utils.physics import (
    calculate_solar_zenith,
    calculate_clear_sky_irradiance,
    calculate_power_output
)
from app.core.config import settings
import os

class ForecastResult:
    """Container for forecast results"""
    def __init__(self):
        self.timestamp = datetime.utcnow()
        self.predictions = []
        self.confidence = 0.85
        self.cloud_data = {}
        self.current_irradiance = 0
        self.current_power_output = 0
        self.location = {}
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'predictions': self.predictions,
            'confidence': self.confidence,
            'cloud_data': self.cloud_data,
            'current_irradiance': self.current_irradiance,
            'current_power_output': self.current_power_output,
            'location': self.location
        }
    
    def generate_alerts(self) -> List[Dict]:
        """Generate alerts based on forecast"""
        alerts = []
        
        # Check for significant power drops
        for i, pred in enumerate(self.predictions):
            if i > 0:
                prev_power = self.predictions[i-1]['power_output']
                curr_power = pred['power_output']
                drop_percent = ((prev_power - curr_power) / prev_power * 100) if prev_power > 0 else 0
                
                if drop_percent > settings.ALERT_THRESHOLD_PERCENT:
                    alerts.append({
                        'severity': 'warning',
                        'message': f"Expected power drop of {drop_percent:.1f}% at {pred['time']}",
                        'timestamp': self.timestamp,
                        'action': 'Consider starting diesel generator'
                    })
        
        return alerts

class IrradiancePredictor:
    """
    Main service orchestrating the entire forecasting pipeline.
    """
    def __init__(self):
        self.satellite_ingester = SatelliteDataIngester(use_mock=settings.USE_MOCK_DATA)
        
        # Load models
        device = 'cuda' if settings.USE_GPU and torch.cuda.is_available() else 'cpu'
        
        cloud_model_path = settings.CLOUD_SEGMENTATION_MODEL_PATH if os.path.exists(settings.CLOUD_SEGMENTATION_MODEL_PATH) else None
        self.cloud_detector = CloudSegmentationInference(cloud_model_path, device=device)
        
        self.motion_tracker = CloudMotionTracker()
        
        irr_model_path = settings.IRRADIANCE_MODEL_PATH if os.path.exists(settings.IRRADIANCE_MODEL_PATH) else None
        self.irradiance_model = IrradianceInference(irr_model_path, device=device)
    
    async def predict_irradiance(self, lat: float, lon: float, 
                                  capacity_kw: float = 50.0,
                                  current_conditions: dict = None) -> ForecastResult:
        """
        End-to-end prediction pipeline.
        
        Args:
            lat: Latitude
            lon: Longitude
            capacity_kw: Rated capacity in kW
            current_conditions: Dict with irradiance, temperature, humidity
        
        Returns:
            ForecastResult with predictions for each time horizon
        """
        result = ForecastResult()
        result.location = {'lat': lat, 'lon': lon}
        
        # Default current conditions if not provided
        if current_conditions is None:
            current_conditions = {
                'irradiance': 850.0,
                'temperature': 32.0,
                'humidity': 45.0
            }
        
        # Step 1: Fetch satellite imagery
        current_image = await self.satellite_ingester.fetch_latest_image(lat, lon)
        past_images = await self.satellite_ingester.fetch_historical_images(lat, lon, count=3)
        
        # Step 2: Detect clouds
        cloud_mask = self.cloud_detector.predict(current_image)
        
        # Step 3: Track cloud motion
        if len(past_images) > 1:
            motion_vectors = self.motion_tracker.estimate_motion(past_images[-1], current_image)
        else:
            motion_vectors = np.zeros((256, 256, 2))
        
        # Step 4: Extract features for ML model
        features = self._extract_features(
            cloud_mask, motion_vectors, lat, lon, current_conditions
        )
        
        # Step 5: Generate physics parameters
        physics_params = self._get_physics_params(lat, lon)
        
        # Step 6: Run irradiance prediction
        predictions_array = self.irradiance_model.predict(
            features.reshape(1, -1),
            physics_params
        )
        
        # Step 7: Generate forecasts for different horizons
        result.current_irradiance = current_conditions['irradiance']
        result.current_power_output = calculate_power_output(
            current_conditions['irradiance'],
            panel_area=capacity_kw * 5.5,  # Assume 5.5 m²/kW
            temperature=current_conditions['temperature'],
            capacity_kw=capacity_kw
        )
        
        for i, horizon_minutes in enumerate(settings.FORECAST_HORIZONS):
            # Scale predictions based on time horizon (simple approach)
            scale_factor = 1.0 - (horizon_minutes / 120.0) * 0.1  # Slight degradation over time
            
            forecast_time = result.timestamp + timedelta(minutes=horizon_minutes)
            
            p10 = predictions_array[0, 0] * scale_factor
            p50 = predictions_array[0, 1] * scale_factor
            p90 = predictions_array[0, 2] * scale_factor
            
            # Calculate power output
            power_10 = calculate_power_output(p10, capacity_kw * 5.5, current_conditions['temperature'], capacity_kw)
            power_50 = calculate_power_output(p50, capacity_kw * 5.5, current_conditions['temperature'], capacity_kw)
            power_90 = calculate_power_output(p90, capacity_kw * 5.5, current_conditions['temperature'], capacity_kw)
            
            result.predictions.append({
                'time': forecast_time.strftime('%H:%M'),
                'timestamp': forecast_time,
                'p10': float(p10),
                'p50': float(p50),
                'p90': float(p90),
                'power_output': float(power_50)
            })
        
        # Step 8: Store cloud data for visualization
        result.cloud_data = {
            'cloud_map': self._downsample_mask(cloud_mask, target_size=(64, 64)),
            'motion_vectors': self._downsample_vectors(motion_vectors, target_size=(64, 64))
        }
        
        return result
    
    def _extract_features(self, cloud_mask, motion_vectors, lat, lon, current_conditions):
        """Extract 15 features for ML model input"""
        features = []
        
        # Cloud features
        avg_opacity = np.mean(cloud_mask) / 3.0  # Normalize to 0-1
        cloud_coverage = np.mean(cloud_mask > 0)
        max_opacity = np.max(cloud_mask) / 3.0
        
        features.append(avg_opacity)
        features.append(cloud_coverage)
        
        # Solar geometry
        solar_zenith = calculate_solar_zenith(lat, lon)
        clear_sky = calculate_clear_sky_irradiance(solar_zenith)
        
        features.append(solar_zenith)
        features.append(clear_sky)
        
        # Current conditions
        features.append(current_conditions.get('irradiance', 850.0) / 1000.0)  # Normalize
        features.append(current_conditions.get('temperature', 32.0) / 50.0)
        features.append(current_conditions.get('humidity', 45.0) / 100.0)
        features.append(current_conditions.get('wind_speed', 3.5) / 20.0)
        
        # Time features
        now = datetime.utcnow()
        hour = now.hour + now.minute / 60.0
        features.append(hour / 24.0)
        features.append(now.month / 12.0)  # Season proxy
        
        # Additional cloud features
        features.append(max_opacity)
        features.append(np.std(cloud_mask) / 3.0)
        
        # Location
        features.append(lat / 90.0)
        
        # Motion features
        motion_magnitude = np.sqrt(motion_vectors[:, :, 0]**2 + motion_vectors[:, :, 1]**2)
        features.append(np.mean(motion_magnitude) / 10.0)  # Normalize
        features.append(0.5)  # Placeholder for cloud distance
        
        return np.array(features, dtype=np.float32)
    
    def _get_physics_params(self, lat, lon):
        """Calculate physics parameters for PINN model"""
        zenith = calculate_solar_zenith(lat, lon)
        
        return {
            'zenith_angle': torch.tensor([zenith], dtype=torch.float32),
            'cloud_opacity': torch.tensor([0.3], dtype=torch.float32)  # Average estimate
        }
    
    def _downsample_mask(self, mask, target_size=(64, 64)):
        """Downsample mask for efficient transmission"""
        from scipy.ndimage import zoom
        factor = (target_size[0] / mask.shape[0], target_size[1] / mask.shape[1])
        downsampled = zoom(mask, factor, order=0)
        return downsampled.tolist()
    
    def _downsample_vectors(self, vectors, target_size=(64, 64)):
        """Downsample motion vectors"""
        from scipy.ndimage import zoom
        factor = (target_size[0] / vectors.shape[0], target_size[1] / vectors.shape[1], 1)
        downsampled = zoom(vectors, factor, order=1)
        
        # Convert to list of dicts
        result = []
        for i in range(downsampled.shape[0]):
            row = []
            for j in range(downsampled.shape[1]):
                row.append({'x': float(downsampled[i, j, 0]), 'y': float(downsampled[i, j, 1])})
            result.append(row)
        
        return result


