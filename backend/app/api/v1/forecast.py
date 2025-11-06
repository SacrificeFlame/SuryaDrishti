from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import ForecastRequest, ForecastResponse, ForecastPoint, AlertData, CloudData
from app.models.database import Forecast as ForecastModel, Microgrid
from app.services.irradiance_predictor import IrradiancePredictor
from typing import List
from datetime import datetime
import json

router = APIRouter()

# Initialize predictor (singleton)
predictor = IrradiancePredictor()

@router.post("/generate", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest, db: Session = Depends(get_db)):
    """
    Generate solar irradiance forecast for next 60 minutes.
    Returns P10, P50, P90 quantiles with confidence intervals.
    """
    try:
        # Get microgrid capacity if coordinates match a known microgrid
        microgrid = db.query(Microgrid).filter(
            Microgrid.latitude == request.latitude,
            Microgrid.longitude == request.longitude
        ).first()
        
        capacity_kw = microgrid.capacity_kw if microgrid else 50.0
        
        # Generate forecast
        result = await predictor.predict_irradiance(
            lat=request.latitude,
            lon=request.longitude,
            capacity_kw=capacity_kw,
            current_conditions={
                'irradiance': request.current_conditions.irradiance,
                'temperature': request.current_conditions.temperature,
                'humidity': request.current_conditions.humidity,
                'wind_speed': request.current_conditions.wind_speed or 3.5
            }
        )
        
        # Save to database
        if microgrid:
            # Convert datetime objects to ISO strings for JSON serialization
            predictions_for_db = []
            for p in result.predictions:
                pred_copy = p.copy()
                if isinstance(pred_copy.get('timestamp'), datetime):
                    pred_copy['timestamp'] = pred_copy['timestamp'].isoformat()
                predictions_for_db.append(pred_copy)
            
            forecast_record = ForecastModel(
                microgrid_id=microgrid.id,
                timestamp=result.timestamp,
                predictions=json.dumps(predictions_for_db),
                cloud_data=json.dumps(result.cloud_data),
                confidence_score=result.confidence
            )
            db.add(forecast_record)
            db.commit()
        
        # Convert to response model
        forecast_points = [
            ForecastPoint(
                time=p['time'],
                timestamp=p['timestamp'],
                p10=p['p10'],
                p50=p['p50'],
                p90=p['p90'],
                power_output=p['power_output']
            ) for p in result.predictions
        ]
        
        alerts = [
            AlertData(
                severity=a['severity'],
                message=a['message'],
                timestamp=a['timestamp'],
                action=a.get('action')
            ) for a in result.generate_alerts()
        ]
        
        cloud_data = CloudData(
            cloud_map=result.cloud_data['cloud_map'],
            motion_vectors=result.cloud_data['motion_vectors']
        )
        
        return ForecastResponse(
            location={'lat': request.latitude, 'lon': request.longitude},
            timestamp=result.timestamp,
            forecasts=forecast_points,
            confidence=result.confidence,
            alerts=alerts,
            cloud_data=cloud_data,
            current_irradiance=result.current_irradiance,
            current_power_output=result.current_power_output
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@router.get("/current/{microgrid_id}", response_model=ForecastResponse)
async def get_current_forecast(microgrid_id: str, db: Session = Depends(get_db)):
    """
    Retrieve cached current forecast for a microgrid.
    """
    # Get microgrid
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail="Microgrid not found")
    
    # Get latest forecast
    latest = db.query(ForecastModel).filter(
        ForecastModel.microgrid_id == microgrid_id
    ).order_by(ForecastModel.timestamp.desc()).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No forecast available for this microgrid")
    
    # Parse stored data
    predictions = json.loads(latest.predictions) if isinstance(latest.predictions, str) else latest.predictions
    cloud_data = json.loads(latest.cloud_data) if isinstance(latest.cloud_data, str) else latest.cloud_data
    
    # Convert to response
    forecast_points = [
        ForecastPoint(
            time=p['time'],
            timestamp=datetime.fromisoformat(p['timestamp']) if isinstance(p['timestamp'], str) else p['timestamp'],
            p10=p['p10'],
            p50=p['p50'],
            p90=p['p90'],
            power_output=p['power_output']
        ) for p in predictions
    ]
    
    # Calculate current values from first forecast point
    current_irr = predictions[0]['p50'] if predictions else 850.0
    current_power = predictions[0]['power_output'] if predictions else 40.0
    
    return ForecastResponse(
        location={'lat': microgrid.latitude, 'lon': microgrid.longitude},
        timestamp=latest.timestamp,
        forecasts=forecast_points,
        confidence=latest.confidence_score or 0.85,
        alerts=[],
        cloud_data=CloudData(**cloud_data) if cloud_data else None,
        current_irradiance=current_irr,
        current_power_output=current_power
    )

@router.get("/history/{microgrid_id}")
async def get_forecast_history(microgrid_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get historical forecasts for a microgrid.
    """
    forecasts = db.query(ForecastModel).filter(
        ForecastModel.microgrid_id == microgrid_id
    ).order_by(ForecastModel.timestamp.desc()).limit(limit).all()
    
    if not forecasts:
        return []
    
    return [
        {
            'id': f.id,
            'timestamp': f.timestamp.isoformat(),
            'confidence': f.confidence_score,
            'predictions_count': len(json.loads(f.predictions) if isinstance(f.predictions, str) else f.predictions)
        } for f in forecasts
    ]


