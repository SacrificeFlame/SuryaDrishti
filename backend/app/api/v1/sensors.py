from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import SensorReadingRequest, SensorReadingResponse
from app.models.database import SensorReading
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/reading", response_model=SensorReadingResponse)
async def ingest_sensor_reading(reading: SensorReadingRequest, db: Session = Depends(get_db)):
    """
    Ingest sensor data from microgrid.
    """
    sensor_reading = SensorReading(
        microgrid_id=reading.microgrid_id,
        timestamp=datetime.utcnow(),
        irradiance=reading.irradiance,
        power_output=reading.power_output,
        temperature=reading.temperature,
        humidity=reading.humidity,
        wind_speed=reading.wind_speed,
        wind_direction=reading.wind_direction
    )
    
    db.add(sensor_reading)
    db.commit()
    db.refresh(sensor_reading)
    
    return SensorReadingResponse(
        id=sensor_reading.id,
        microgrid_id=sensor_reading.microgrid_id,
        timestamp=sensor_reading.timestamp,
        irradiance=sensor_reading.irradiance,
        power_output=sensor_reading.power_output,
        temperature=sensor_reading.temperature,
        humidity=sensor_reading.humidity,
        wind_speed=sensor_reading.wind_speed,
        wind_direction=sensor_reading.wind_direction
    )

@router.get("/{microgrid_id}/latest", response_model=SensorReadingResponse)
async def get_latest_reading(microgrid_id: str, db: Session = Depends(get_db)):
    """
    Get latest sensor reading for a microgrid.
    """
    reading = db.query(SensorReading).filter(
        SensorReading.microgrid_id == microgrid_id
    ).order_by(SensorReading.timestamp.desc()).first()
    
    if not reading:
        raise HTTPException(status_code=404, detail="No sensor readings found")
    
    return SensorReadingResponse(
        id=reading.id,
        microgrid_id=reading.microgrid_id,
        timestamp=reading.timestamp,
        irradiance=reading.irradiance,
        power_output=reading.power_output,
        temperature=reading.temperature,
        humidity=reading.humidity,
        wind_speed=reading.wind_speed,
        wind_direction=reading.wind_direction
    )

@router.get("/{microgrid_id}/history", response_model=List[SensorReadingResponse])
async def get_sensor_history(microgrid_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get historical sensor readings.
    """
    readings = db.query(SensorReading).filter(
        SensorReading.microgrid_id == microgrid_id
    ).order_by(SensorReading.timestamp.desc()).limit(limit).all()
    
    return [
        SensorReadingResponse(
            id=r.id,
            microgrid_id=r.microgrid_id,
            timestamp=r.timestamp,
            irradiance=r.irradiance,
            power_output=r.power_output,
            temperature=r.temperature,
            humidity=r.humidity,
            wind_speed=r.wind_speed,
            wind_direction=r.wind_direction
        ) for r in readings
    ]

