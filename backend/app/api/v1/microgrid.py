from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import MicrogridInfo, SystemStatus
from app.models.database import Microgrid
from typing import List
from datetime import datetime
import random

router = APIRouter()

@router.get("/{microgrid_id}", response_model=MicrogridInfo)
async def get_microgrid(microgrid_id: str, db: Session = Depends(get_db)):
    """
    Get microgrid information.
    """
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail="Microgrid not found")
    
    return MicrogridInfo(
        id=microgrid.id,
        name=microgrid.name,
        latitude=microgrid.latitude,
        longitude=microgrid.longitude,
        capacity_kw=microgrid.capacity_kw,
        created_at=microgrid.created_at
    )

@router.get("/{microgrid_id}/status", response_model=SystemStatus)
async def get_system_status(microgrid_id: str, db: Session = Depends(get_db)):
    """
    Get current system status (battery, diesel, loads).
    """
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail="Microgrid not found")
    
    # Mock system status (in production, fetch from actual controllers)
    status = SystemStatus(
        battery={
            'soc': random.uniform(60, 95),  # State of charge %
            'voltage': random.uniform(48, 54),  # Volts
            'current': random.uniform(-10, 10)  # Amps (negative = charging)
        },
        diesel={
            'status': 'standby' if random.random() > 0.2 else 'running',
            'fuelLevel': random.uniform(40, 100)  # %
        },
        loads={
            'critical': random.uniform(10, 25),  # kW
            'nonCritical': random.uniform(5, 15)  # kW
        },
        timestamp=datetime.utcnow(),
        recent_actions=[
            {
                'action': 'Battery charging',
                'timestamp': datetime.utcnow().isoformat(),
                'details': 'Solar surplus stored'
            },
            {
                'action': 'Load balancing',
                'timestamp': datetime.utcnow().isoformat(),
                'details': 'Non-critical loads adjusted'
            }
        ]
    )
    
    return status

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


