import torch
import torch.nn as nn
import numpy as np

class PhysicsInformedIrradianceModel(nn.Module):
    """
    Physics-Informed Neural Network for solar irradiance prediction.
    Combines learned patterns with radiative transfer physics.
    """
    def __init__(self, input_features=15, output_quantiles=3):
        super().__init__()
        
        # Neural network component
        self.nn_encoder = nn.Sequential(
            nn.Linear(input_features, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        
        # Separate heads for each quantile (P10, P50, P90)
        self.quantile_heads = nn.ModuleList([
            nn.Linear(64, 1) for _ in range(output_quantiles)
        ])
        
    def forward(self, x, physics_params=None):
        """
        Args:
            x: (batch, 15) feature tensor
                Features: [cloud_opacity, cloud_distance, solar_zenith, 
                          current_irradiance, temp, humidity, wind_speed,
                          aerosol_depth, time_of_day, season, ...]
            physics_params: dict with 'zenith_angle', 'cloud_opacity', etc.
        
        Returns:
            predictions: (batch, 3) tensor with [P10, P50, P90] irradiance values
        """
        # Neural network prediction
        features = self.nn_encoder(x)
        nn_outputs = torch.stack([head(features) for head in self.quantile_heads], dim=1).squeeze(-1)
        
        # Physics-based prediction (if parameters provided)
        if physics_params is not None:
            physics_pred = self.physics_model(physics_params)
            # Weighted combination (learnable weights)
            combined = 0.6 * nn_outputs + 0.4 * physics_pred
            return combined
        
        return nn_outputs
    
    def physics_model(self, params):
        """
        Calculate clear-sky irradiance attenuated by clouds.
        
        I = I0 * cos(θ) * exp(-τ * m)
        where:
            I0 = 1367 W/m² (solar constant)
            θ = solar zenith angle
            τ = cloud optical depth
            m = air mass
        """
        I0 = 1367  # W/m²
        zenith = params['zenith_angle']
        cloud_opacity = params['cloud_opacity']
        
        # Air mass calculation (simplified)
        cos_zenith = torch.cos(zenith)
        air_mass = torch.where(cos_zenith > 0.01, 1 / cos_zenith, torch.tensor(0.0))
        
        # Clear sky irradiance
        clear_sky = I0 * cos_zenith * torch.exp(-0.15 * air_mass)
        
        # Cloud attenuation
        irradiance = clear_sky * torch.exp(-cloud_opacity)
        
        # Ensure non-negative
        irradiance = torch.clamp(irradiance, min=0.0)
        
        return irradiance.unsqueeze(1).repeat(1, 3)  # Repeat for 3 quantiles


class IrradianceInference:
    """Inference wrapper for irradiance forecasting"""
    def __init__(self, model_path: str = None, device='cpu'):
        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
        self.model = PhysicsInformedIrradianceModel(input_features=15, output_quantiles=3)
        
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            except FileNotFoundError:
                print(f"Warning: Model file not found at {model_path}. Using untrained model.")
        
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, features: np.ndarray, physics_params: dict = None) -> np.ndarray:
        """
        Predict irradiance quantiles
        
        Args:
            features: (N, 15) array of features
            physics_params: Optional dict with zenith_angle and cloud_opacity tensors
            
        Returns:
            predictions: (N, 3) array with [P10, P50, P90]
        """
        with torch.no_grad():
            features_tensor = torch.from_numpy(features).float().to(self.device)
            
            if physics_params:
                # Convert numpy arrays to tensors if needed
                for key in physics_params:
                    if isinstance(physics_params[key], np.ndarray):
                        physics_params[key] = torch.from_numpy(physics_params[key]).float().to(self.device)
            
            predictions = self.model(features_tensor, physics_params)
            
        return predictions.cpu().numpy()
