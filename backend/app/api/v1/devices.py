"""
Device Management API endpoints
Handles CRUD operations for devices.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.database import Device, Microgrid
from app.models.schemas import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse
)

router = APIRouter()


@router.post("/microgrid/{microgrid_id}/devices", response_model=DeviceResponse, status_code=201)
async def create_device(
    microgrid_id: str,
    device: DeviceCreate,
    db: Session = Depends(get_db)
):
    """Create a new device for a microgrid."""
    # Verify microgrid exists
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
    
    # Validate device type
    if device.device_type not in ['essential', 'flexible', 'optional']:
        raise HTTPException(
            status_code=400,
            detail="device_type must be 'essential', 'flexible', or 'optional'"
        )
    
    # Create device
    db_device = Device(
        microgrid_id=microgrid_id,
        name=device.name,
        power_consumption_watts=device.power_consumption_watts,
        device_type=device.device_type,
        minimum_runtime_minutes=device.minimum_runtime_minutes,
        preferred_hours=device.preferred_hours,
        priority_level=device.priority_level,
        is_active=True
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device


@router.get("/microgrid/{microgrid_id}/devices", response_model=List[DeviceResponse])
async def get_devices(
    microgrid_id: str,
    active_only: bool = Query(False, description="Return only active devices"),
    db: Session = Depends(get_db)
):
    """Get all devices for a microgrid."""
    query = db.query(Device).filter(Device.microgrid_id == microgrid_id)
    
    if active_only:
        query = query.filter(Device.is_active == True)
    
    devices = query.order_by(Device.priority_level, Device.device_type).all()
    return devices


@router.get("/microgrid/{microgrid_id}/devices/{device_id}", response_model=DeviceResponse)
async def get_device(
    microgrid_id: str,
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific device."""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.microgrid_id == microgrid_id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device


@router.put("/microgrid/{microgrid_id}/devices/{device_id}", response_model=DeviceResponse)
async def update_device(
    microgrid_id: str,
    device_id: int,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """Update a device."""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.microgrid_id == microgrid_id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update fields
    update_data = device_update.dict(exclude_unset=True)
    
    if 'device_type' in update_data:
        if update_data['device_type'] not in ['essential', 'flexible', 'optional']:
            raise HTTPException(
                status_code=400,
                detail="device_type must be 'essential', 'flexible', or 'optional'"
            )
    
    for field, value in update_data.items():
        setattr(device, field, value)
    
    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)
    
    return device


@router.delete("/microgrid/{microgrid_id}/devices/{device_id}", status_code=204)
async def delete_device(
    microgrid_id: str,
    device_id: int,
    db: Session = Depends(get_db)
):
    """Delete a device."""
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.microgrid_id == microgrid_id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    
    return None

