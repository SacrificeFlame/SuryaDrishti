"""
System Configuration API endpoints
Handles system configuration management.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.models.database import SystemConfiguration, Microgrid
from app.models.schemas import (
    SystemConfigurationResponse,
    SystemConfigurationUpdate
)

router = APIRouter()


@router.get("/microgrid/{microgrid_id}/configuration", response_model=SystemConfigurationResponse)
async def get_configuration(
    microgrid_id: str,
    db: Session = Depends(get_db)
):
    """Get system configuration for a microgrid."""
    # Verify microgrid exists
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
    
    config = db.query(SystemConfiguration).filter(
        SystemConfiguration.microgrid_id == microgrid_id
    ).first()
    
    if not config:
        # Create default configuration
        config = SystemConfiguration(
            microgrid_id=microgrid_id,
            battery_capacity_kwh=50.0,
            battery_max_charge_rate_kw=10.0,
            battery_max_discharge_rate_kw=10.0,
            battery_efficiency=0.95,
            battery_min_soc=0.2,
            battery_max_soc=0.95,
            grid_peak_rate_per_kwh=10.0,
            grid_off_peak_rate_per_kwh=5.0,
            grid_peak_hours={'start': 8, 'end': 20},
            grid_export_rate_per_kwh=4.0,
            grid_export_enabled=True,
            generator_fuel_consumption_l_per_kwh=0.25,
            generator_fuel_cost_per_liter=80.0,
            generator_min_runtime_minutes=30,
            generator_max_power_kw=20.0,
            optimization_mode='cost',
            safety_margin_critical_loads=0.1
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config


@router.put("/microgrid/{microgrid_id}/configuration", response_model=SystemConfigurationResponse)
async def update_configuration(
    microgrid_id: str,
    config_update: SystemConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Update system configuration for a microgrid."""
    # Verify microgrid exists
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
    
    config = db.query(SystemConfiguration).filter(
        SystemConfiguration.microgrid_id == microgrid_id
    ).first()
    
    if not config:
        # Create new configuration
        config = SystemConfiguration(microgrid_id=microgrid_id)
        db.add(config)
    
    # Update fields
    update_data = config_update.dict(exclude_unset=True)
    
    # Validate optimization_mode
    if 'optimization_mode' in update_data:
        valid_modes = ['cost', 'battery_longevity', 'grid_independence']
        if update_data['optimization_mode'] not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"optimization_mode must be one of: {', '.join(valid_modes)}"
            )
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    return config

