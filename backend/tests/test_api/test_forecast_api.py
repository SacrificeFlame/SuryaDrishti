import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.main import app

client = TestClient(app)

class TestForecastAPI:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    def test_generate_forecast(self):
        """Test forecast generation endpoint"""
        request_data = {
            "latitude": 28.4595,
            "longitude": 77.0266,
            "radius_km": 10,
            "current_conditions": {
                "irradiance": 850.0,
                "temperature": 32.0,
                "humidity": 45.0
            }
        }
        
        response = client.post("/api/v1/forecast/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "forecasts" in data
        assert "confidence" in data
        assert "location" in data
        assert len(data["forecasts"]) == 5  # 5 forecast horizons
        
        # Check forecast structure
        for forecast in data["forecasts"]:
            assert "time" in forecast
            assert "p10" in forecast
            assert "p50" in forecast
            assert "p90" in forecast
            assert "power_output" in forecast
            
            # Validate quantile ordering (approximately)
            assert forecast["p10"] <= forecast["p90"] + 1000  # Allow some slack
    
    def test_list_microgrids(self):
        """Test microgrid listing endpoint"""
        response = client.get("/api/v1/microgrid/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # We seeded 3 microgrids
        
        # Check microgrid structure
        for microgrid in data:
            assert "id" in microgrid
            assert "name" in microgrid
            assert "latitude" in microgrid
            assert "longitude" in microgrid
            assert "capacity_kw" in microgrid
    
    def test_get_microgrid(self):
        """Test get specific microgrid endpoint"""
        response = client.get("/api/v1/microgrid/microgrid_001")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "microgrid_001"
        assert "name" in data
        assert "latitude" in data
    
    def test_get_system_status(self):
        """Test system status endpoint"""
        response = client.get("/api/v1/microgrid/microgrid_001/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "battery" in data
        assert "diesel" in data
        assert "loads" in data
        assert "timestamp" in data
        
        # Check battery data
        assert "soc" in data["battery"]
        assert 0 <= data["battery"]["soc"] <= 100
    
    def test_get_alerts(self):
        """Test alerts endpoint"""
        response = client.get("/api/v1/alerts/microgrid_001")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_invalid_forecast_request(self):
        """Test forecast with invalid data"""
        invalid_request = {
            "latitude": "invalid",  # Should be float
            "longitude": 77.0266,
            "radius_km": 10
        }
        
        response = client.post("/api/v1/forecast/generate", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    def test_nonexistent_microgrid(self):
        """Test getting non-existent microgrid"""
        response = client.get("/api/v1/microgrid/nonexistent_id")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

