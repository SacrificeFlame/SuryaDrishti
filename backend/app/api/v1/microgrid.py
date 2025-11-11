from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import MicrogridInfo, SystemStatus
from app.models.database import Microgrid
from typing import List
from datetime import datetime
import random
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{microgrid_id}", response_model=MicrogridInfo)
async def get_microgrid(microgrid_id: str, db: Session = Depends(get_db), response: Response = None):
    """
    Get microgrid information.
    """
    try:
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            # Log detailed error information
            all_microgrids = db.query(Microgrid).all()
            logger.error(f"Microgrid {microgrid_id} not found. Available microgrids: {[mg.id for mg in all_microgrids]}")
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found. Available microgrids: {[mg.id for mg in all_microgrids]}")
        
        return MicrogridInfo(
            id=microgrid.id,
            name=microgrid.name,
            latitude=microgrid.latitude,
            longitude=microgrid.longitude,
            capacity_kw=microgrid.capacity_kw,
            created_at=microgrid.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting microgrid {microgrid_id}: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{microgrid_id}/status", response_model=SystemStatus)
async def get_system_status(microgrid_id: str, db: Session = Depends(get_db)):
    """
    Get current system status (battery, diesel, loads).
    """
    try:
        # Check if microgrid exists (but don't fail if it doesn't)
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        
        # Calculate uptime from microgrid creation date
        uptime_hours = None
        if microgrid and microgrid.created_at:
            time_diff = datetime.utcnow() - microgrid.created_at
            uptime_hours = time_diff.total_seconds() / 3600.0  # Convert to hours
        else:
            # Default uptime if microgrid not found (assume system started 30 days ago)
            uptime_hours = 30 * 24  # 30 days in hours
        
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        # Get real sensor data for status
        from app.models.database import SensorReading
        latest_reading = db.query(SensorReading).filter(
            SensorReading.microgrid_id == microgrid_id
        ).order_by(SensorReading.timestamp.desc()).first()
        
        # Get real battery SOC from latest reading or use default
        battery_soc = 50.0
        battery_voltage = 48.0
        battery_current = 0.0
        
        if latest_reading:
            # Estimate SOC from power output (simplified)
            if latest_reading.power_output > 0:
                battery_current = -5.0  # Charging
                battery_soc = min(95.0, 50.0 + (latest_reading.power_output / microgrid.capacity_kw) * 10)
            else:
                battery_current = 2.0  # Discharging
                battery_soc = max(20.0, 50.0 - 5.0)
            battery_voltage = 48.0 + (battery_soc / 100.0) * 6.0
        
        # Get real load data (simplified - in production, get from device table)
        from app.models.database import Device
        devices = db.query(Device).filter(
            Device.microgrid_id == microgrid_id,
            Device.is_active == True
        ).all()
        
        total_load = sum(d.power_consumption_watts or 0 for d in devices) / 1000.0  # Convert to kW
        critical_load = sum(d.power_consumption_watts or 0 for d in devices if d.device_type == 'essential') / 1000.0
        non_critical_load = total_load - critical_load
        
        return SystemStatus(
            battery={
                'soc': battery_soc,
                'voltage': battery_voltage,
                'current': battery_current
            },
            diesel={
                'status': 'off',
                'fuelLevel': 80.0  # Default - should come from actual controller
            },
            loads={
                'critical': critical_load,
                'nonCritical': non_critical_load
            },
            timestamp=datetime.utcnow(),
            recent_actions=[
                {
                    'action': 'System operational',
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': f'Solar: {latest_reading.power_output if latest_reading else 0:.2f}kW, Load: {total_load:.2f}kW'
                }
            ],
            uptime_hours=uptime_hours
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system status for {microgrid_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{microgrid_id}/status/diesel")
async def update_diesel_status(
    microgrid_id: str,
    status: str = Query(..., description="Generator status: 'on', 'off', 'standby', or 'running'"),
    db: Session = Depends(get_db)
):
    """
    Update diesel generator status.
    """
    try:
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        # Validate status
        if status not in ['on', 'off', 'standby', 'running']:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'on', 'off', 'standby', or 'running'")
        
        # Map 'on' to 'running' for consistency
        mapped_status = 'running' if status == 'on' else status
        
        # In a real system, this would control the actual generator
        # For now, we'll just return success
        logger.info(f"Diesel generator status updated for {microgrid_id}: {mapped_status}")
        
        return {
            "status": "success",
            "microgrid_id": microgrid_id,
            "diesel_status": mapped_status,
            "message": f"Diesel generator set to {mapped_status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating diesel status for {microgrid_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update diesel status: {str(e)}")

@router.get("/", response_model=List[MicrogridInfo])
async def list_microgrids(db: Session = Depends(get_db)):
    """
    List all microgrids.
    """
    microgrids = db.query(Microgrid).all()
    
    return [
        MicrogridInfo(
            id=mg.id,
            name=mg.name,
            latitude=mg.latitude,
            longitude=mg.longitude,
            capacity_kw=mg.capacity_kw,
            created_at=mg.created_at
        ) for mg in microgrids
    ]


