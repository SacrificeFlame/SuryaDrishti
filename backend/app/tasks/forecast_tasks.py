from celery import shared_task
from app.services.irradiance_predictor import IrradiancePredictor
from app.models.database import Forecast, Microgrid
from app.core.database import SessionLocal
import asyncio
import json
from datetime import datetime

@shared_task
def generate_forecast_task(microgrid_id: str):
    """
    Background task to generate forecast every 15 minutes.
    """
    predictor = IrradiancePredictor()
    db = SessionLocal()
    
    try:
        # Get microgrid details
        if microgrid_id == 'all_microgrids':
            microgrids = db.query(Microgrid).all()
        else:
            microgrids = [db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()]
        
        for microgrid in microgrids:
            if not microgrid:
                continue
            
            # Run prediction (need to handle async in sync context)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                forecast_result = loop.run_until_complete(
                    predictor.predict_irradiance(
                        lat=microgrid.latitude,
                        lon=microgrid.longitude,
                        capacity_kw=microgrid.capacity_kw
                    )
                )
                
                # Save to database
                forecast = Forecast(
                    microgrid_id=microgrid.id,
                    timestamp=forecast_result.timestamp,
                    predictions=json.dumps([p for p in forecast_result.predictions]),
                    cloud_data=json.dumps(forecast_result.cloud_data),
                    confidence_score=forecast_result.confidence
                )
                db.add(forecast)
                db.commit()
                
                print(f"[SUCCESS] Forecast generated for {microgrid.id}")
                
            finally:
                loop.close()
        
    except Exception as e:
        print(f"[ERROR] Error generating forecast: {e}")
        db.rollback()
    finally:
        db.close()

@shared_task
def retrain_models_task():
    """
    Weekly task to retrain models with latest data.
    """
    print("[INFO] Starting model retraining...")
    
    # Import training functions
    from app.ml.models.cloud_segmentation.train import train_cloud_segmentation
    from app.ml.models.irradiance_forecast.train import train_irradiance_model
    
    try:
        # Retrain cloud segmentation model
        train_cloud_segmentation(
            data_dir='data/processed',
            epochs=20,
            batch_size=4
        )
        
        # Retrain irradiance model
        train_irradiance_model(
            data_path='data/processed/irradiance_data.npz',
            epochs=50,
            batch_size=64
        )
        
        print("[SUCCESS] Model retraining complete!")
        
    except Exception as e:
        print(f"[ERROR] Error during retraining: {e}")

