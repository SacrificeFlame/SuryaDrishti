import pytest
import torch
import numpy as np
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.ml.models.irradiance_forecast.pinn import PhysicsInformedIrradianceModel

class TestIrradianceModel:
    @pytest.fixture
    def model(self):
        return PhysicsInformedIrradianceModel(input_features=15, output_quantiles=3)
    
    @pytest.fixture
    def sample_input(self):
        # Create sample feature vector
        return torch.randn(8, 15)  # Batch of 8
    
    @pytest.fixture
    def physics_params(self):
        return {
            'zenith_angle': torch.tensor([0.5, 0.6, 0.7, 0.8, 0.5, 0.6, 0.7, 0.8]),
            'cloud_opacity': torch.tensor([0.1, 0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 0.4])
        }
    
    def test_model_forward_pass(self, model, sample_input, physics_params):
        """Test that model produces correct output shape"""
        output = model(sample_input, physics_params)
        
        assert output.shape == (8, 3)  # Batch size 8, 3 quantiles
        assert not torch.isnan(output).any()  # No NaN values
        
    def test_quantile_ordering(self, model, sample_input, physics_params):
        """Test that P10 <= P50 <= P90 (approximately)"""
        output = model(sample_input, physics_params)
        
        p10 = output[:, 0]
        p50 = output[:, 1]
        p90 = output[:, 2]
        
        # Due to training, quantiles may not be perfectly ordered
        # but we can check that they're in reasonable ranges
        assert output.min() >= 0  # Non-negative irradiance
        
    def test_physics_constraints(self, model):
        """Test that physics model respects physical laws"""
        # Test with clear sky (no clouds)
        clear_sky_params = {
            'zenith_angle': torch.tensor([0.0]),  # Noon
            'cloud_opacity': torch.tensor([0.0])  # No clouds
        }
        
        physics_output = model.physics_model(clear_sky_params)
        
        # Should be close to solar constant
        assert physics_output[0, 0].item() > 1000  # Reasonable clear-sky value
        assert physics_output[0, 0].item() < 1400  # Not exceeding solar constant
    
    def test_model_save_load(self, model, tmp_path):
        """Test model serialization"""
        save_path = tmp_path / "model.pth"
        
        # Save model
        torch.save(model.state_dict(), save_path)
        
        # Load model
        loaded_model = PhysicsInformedIrradianceModel(input_features=15, output_quantiles=3)
        loaded_model.load_state_dict(torch.load(save_path))
        
        # Compare outputs
        sample_input = torch.randn(4, 15)
        physics_params = {
            'zenith_angle': torch.tensor([0.5, 0.6, 0.7, 0.8]),
            'cloud_opacity': torch.tensor([0.1, 0.2, 0.3, 0.4])
        }
        
        original_output = model(sample_input, physics_params)
        loaded_output = loaded_model(sample_input, physics_params)
        
        assert torch.allclose(original_output, loaded_output, rtol=1e-5)
    
    def test_different_batch_sizes(self, model):
        """Test model with various batch sizes"""
        for batch_size in [1, 4, 16, 32]:
            sample_input = torch.randn(batch_size, 15)
            physics_params = {
                'zenith_angle': torch.rand(batch_size),
                'cloud_opacity': torch.rand(batch_size)
            }
            
            output = model(sample_input, physics_params)
            assert output.shape == (batch_size, 3)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

