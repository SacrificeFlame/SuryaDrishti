from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import AlertResponse, AlertAcknowledge
from app.models.database import Alert
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/{microgrid_id}", response_model=List[AlertResponse])
async def get_alerts(microgrid_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get recent alerts for a microgrid.
    """
    alerts = db.query(Alert).filter(
        Alert.microgrid_id == microgrid_id
    ).order_by(Alert.timestamp.desc()).limit(limit).all()
    
    return [
        AlertResponse(
            id=alert.id,
            microgrid_id=alert.microgrid_id,
            timestamp=alert.timestamp,
            severity=alert.severity,
            message=alert.message,
            action_taken=alert.action_taken,
            resolved_at=alert.resolved_at,
            acknowledged=bool(alert.acknowledged)
        ) for alert in alerts
    ]

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, data: AlertAcknowledge, db: Session = Depends(get_db)):
    """
    Acknowledge an alert.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = 1 if data.acknowledged else 0
    db.commit()
    
    return {"status": "success", "alert_id": alert_id, "acknowledged": data.acknowledged}

@router.post("/create")
async def create_alert(microgrid_id: str, severity: str, message: str, 
                       action: str = None, db: Session = Depends(get_db)):
    """
    Create a new alert (internal use by services).
    """
    alert = Alert(
        microgrid_id=microgrid_id,
        timestamp=datetime.utcnow(),
        severity=severity,
        message=message,
        action_taken=action
    )
    db.add(alert)
    db.commit()
    
    return {"status": "success", "alert_id": alert.id}


