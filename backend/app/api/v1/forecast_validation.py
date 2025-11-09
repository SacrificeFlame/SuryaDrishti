"""
Forecast Validation API endpoint
Validates forecast realism and provides assessment.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.models.database import Microgrid
from app.utils.forecast_validator import validate_forecast_realism

router = APIRouter()


class ForecastValidationRequest(BaseModel):
    forecast_data: List[Dict[str, Any]]
    microgrid_id: str = None
    latitude: float = None
    longitude: float = None
    capacity_kw: float = None


@router.post("/forecast/validate")
async def validate_forecast(
    request: ForecastValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate if a solar irradiance and power forecast is realistic.
    
    Either provide microgrid_id OR latitude/longitude/capacity_kw.
    """
    if request.microgrid_id:
        # Get microgrid details
        microgrid = db.query(Microgrid).filter(Microgrid.id == request.microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {request.microgrid_id} not found")
        
        latitude = microgrid.latitude
        longitude = microgrid.longitude
        capacity_kw = microgrid.capacity_kw
        location_name = microgrid.name
    else:
        if not all([request.latitude, request.longitude, request.capacity_kw]):
            raise HTTPException(
                status_code=400,
                detail="Either provide microgrid_id or latitude/longitude/capacity_kw"
            )
        latitude = request.latitude
        longitude = request.longitude
        capacity_kw = request.capacity_kw
        location_name = f"Location at ({latitude}, {longitude})"
    
    # Validate forecast
    result = validate_forecast_realism(
        forecast_data=request.forecast_data,
        latitude=latitude,
        longitude=longitude,
        capacity_kw=capacity_kw,
        location_name=location_name
    )
    
    return result

