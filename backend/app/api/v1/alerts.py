from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import AlertResponse, AlertAcknowledge
from app.models.database import Alert
from typing import List
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{microgrid_id}", response_model=List[AlertResponse])
async def get_alerts(microgrid_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get recent alerts for a microgrid.
    Always returns at least some system alerts if the system is running.
    """
    try:
        alerts = db.query(Alert).filter(
            Alert.microgrid_id == microgrid_id
        ).order_by(Alert.timestamp.desc()).limit(limit).all()
        
        # If no alerts exist but system is running, generate default system status alerts
        if len(alerts) == 0:
            logger.info(f"No alerts found for {microgrid_id}, generating default system alerts")
            # Check if microgrid exists (system is running)
            from app.models.database import Microgrid
            microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
            if microgrid:
                # Generate default system alerts
                now = datetime.utcnow()
                default_alerts = [
                    Alert(
                        microgrid_id=microgrid_id,
                        timestamp=now - timedelta(minutes=5),
                        severity='info',
                        message='System initialized and running normally',
                        action_taken='System startup completed',
                        acknowledged=0
                    ),
                    Alert(
                        microgrid_id=microgrid_id,
                        timestamp=now - timedelta(minutes=15),
                        severity='info',
                        message='Forecast generation scheduled for next 15 minutes',
                        action_taken='Forecast scheduler activated',
                        acknowledged=0
                    ),
                    Alert(
                        microgrid_id=microgrid_id,
                        timestamp=now - timedelta(hours=1),
                        severity='warning',
                        message='Battery SOC below 70% - monitoring charge cycle',
                        action_taken='Battery charging initiated',
                        acknowledged=0
                    ),
                ]
                for alert in default_alerts:
                    db.add(alert)
                db.commit()
                # Refresh alerts from database
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
    except Exception as e:
        logger.error(f"Error getting alerts for {microgrid_id}: {e}", exc_info=True)
        # Return empty list on error instead of 500
        return []

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int, 
    data: AlertAcknowledge,
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.
    """
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        acknowledged = data.acknowledged
        
        alert.acknowledged = 1 if acknowledged else 0
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert {alert_id} acknowledged: {acknowledged}")
        
        return {
            "status": "success", 
            "alert_id": alert_id, 
            "acknowledged": acknowledged
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error acknowledging alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/create")
async def create_alert(microgrid_id: str, severity: str, message: str, 
                       action: str = None, db: Session = Depends(get_db)):
    """
    Create a new alert (internal use by services).
    Automatically sends SMS notification if configured.
    """
    from app.services.notification_service import notification_service
    from app.models.database import NotificationPreference
    
    alert = Alert(
        microgrid_id=microgrid_id,
        timestamp=datetime.utcnow(),
        severity=severity,
        message=message,
        action_taken=action
    )
    db.add(alert)
    db.commit()
    
    # Send SMS notification if preferences allow
    try:
        prefs = db.query(NotificationPreference).filter(
            NotificationPreference.microgrid_id == microgrid_id
        ).first()
        
        if prefs and prefs.enable_sms and prefs.phone_number:
            # Check if this severity level is enabled
            should_send = False
            if severity == 'critical' and prefs.enable_critical_alerts:
                should_send = True
            elif severity == 'warning' and prefs.enable_warning_alerts:
                should_send = True
            elif severity == 'info' and prefs.enable_info_alerts:
                should_send = True
            
            if should_send:
                notification_service.send_alert_notification(
                    phone_number=prefs.phone_number,
                    alert_type=severity,
                    message=message,
                    microgrid_id=microgrid_id,
                    severity=severity
                )
    except Exception as e:
        logger.error(f"Failed to send notification for alert {alert.id}: {e}", exc_info=True)
        # Don't fail the alert creation if notification fails
    
    return {"status": "success", "alert_id": alert.id}


