#!/usr/bin/env python3
"""
System integration test for SuryaDrishti
Tests all components without starting the server
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.services.irradiance_predictor import IrradiancePredictor
from app.core.database import SessionLocal
from app.models.database import Microgrid

async def test_forecast_generation():
    """Test the complete forecasting pipeline"""
    print("=" * 70)
    print("SuryaDrishti - System Integration Test")
    print("=" * 70)
    
    # Test 1: Database
    print("\n[Test 1/4] Testing Database Connection...")
    try:
        db = SessionLocal()
        microgrids = db.query(Microgrid).all()
        print(f"✅ Database OK - Found {len(microgrids)} microgrids")
        for mg in microgrids:
            print(f"   - {mg.id}: {mg.name}")
        db.close()
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False
    
    # Test 2: ML Models
    print("\n[Test 2/4] Testing ML Models...")
    try:
        predictor = IrradiancePredictor()
        print("✅ ML Models Loaded")
        print(f"   - Cloud Segmentation: {predictor.cloud_detector.model.__class__.__name__}")
        print(f"   - Irradiance Forecasting: {predictor.irradiance_model.model.__class__.__name__}")
    except Exception as e:
        print(f"❌ ML Model Error: {e}")
        return False
    
    # Test 3: Forecast Generation
    print("\n[Test 3/4] Generating Test Forecast...")
    try:
        result = await predictor.predict_irradiance(
            lat=28.4595,
            lon=77.0266,
            capacity_kw=50.0,
            current_conditions={
                'irradiance': 850.0,
                'temperature': 32.0,
                'humidity': 45.0
            }
        )
        
        print("✅ Forecast Generated Successfully")
        print(f"   - Location: ({result.location['lat']}, {result.location['lon']})")
        print(f"   - Timestamp: {result.timestamp}")
        print(f"   - Confidence: {result.confidence * 100:.1f}%")
        print(f"   - Current Irradiance: {result.current_irradiance:.1f} W/m²")
        print(f"   - Current Power: {result.current_power_output:.1f} kW")
        print(f"   - Forecast Points: {len(result.predictions)}")
        
        # Display forecast values
        print("\n   Forecast Horizons:")
        for pred in result.predictions[:3]:  # Show first 3
            print(f"     {pred['time']}: P50={pred['p50']:.0f} W/m², Power={pred['power_output']:.1f} kW")
        
        # Check for alerts
        alerts = result.generate_alerts()
        if alerts:
            print(f"\n   ⚠️  Generated {len(alerts)} alerts:")
            for alert in alerts:
                print(f"     - {alert['severity'].upper()}: {alert['message']}")
        else:
            print("\n   ✅ No alerts (stable conditions)")
            
    except Exception as e:
        print(f"❌ Forecast Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Physics Calculations
    print("\n[Test 4/4] Testing Physics Utils...")
    try:
        from app.utils.physics import (
            calculate_solar_zenith,
            calculate_clear_sky_irradiance,
            calculate_power_output
        )
        from datetime import datetime
        
        zenith = calculate_solar_zenith(28.4595, 77.0266, datetime(2024, 6, 15, 12, 0))
        clear_sky = calculate_clear_sky_irradiance(zenith)
        power = calculate_power_output(850, 275, 32, 50)
        
        print("✅ Physics Calculations OK")
        print(f"   - Solar Zenith: {zenith:.3f} rad ({zenith * 180/3.14159:.1f}°)")
        print(f"   - Clear Sky Irradiance: {clear_sky:.1f} W/m²")
        print(f"   - Power Output: {power:.1f} kW")
    except Exception as e:
        print(f"❌ Physics Error: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - System is operational!")
    print("=" * 70)
    print("\nYou can now start the backend server:")
    print("  cd backend && uvicorn app.main:app --reload")
    print("\nOr run a test API request:")
    print("""  curl -X POST "http://localhost:8000/api/v1/forecast/generate" \\
    -H "Content-Type: application/json" \\
    -d '{"latitude": 28.4595, "longitude": 77.0266, "radius_km": 10,
         "current_conditions": {"irradiance": 850, "temperature": 32, "humidity": 45}}'""")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_forecast_generation())
    sys.exit(0 if success else 1)

