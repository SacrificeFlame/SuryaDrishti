"""
Notification API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import NotificationPreference, Microgrid
from app.services.notification_service import notification_service
from typing import Optional, Dict
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class NotificationPreferenceRequest(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None  # Email validation can be added later if needed
    enable_sms: bool = True
    enable_email: bool = False
    enable_critical_alerts: bool = True
    enable_warning_alerts: bool = True
    enable_info_alerts: bool = False
    enable_forecast_updates: bool = False


class SendNotificationRequest(BaseModel):
    phone_number: str
    message: str


@router.get("/preferences/{microgrid_id}")
async def get_notification_preferences(
    microgrid_id: str,
    db: Session = Depends(get_db)
):
    """Get notification preferences for a microgrid"""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.microgrid_id == microgrid_id
    ).first()
    
    if not prefs:
        # Return defaults
        return {
            "microgrid_id": microgrid_id,
            "phone_number": None,
            "email": None,
            "enable_sms": True,
            "enable_email": False,
            "enable_critical_alerts": True,
            "enable_warning_alerts": True,
            "enable_info_alerts": False,
            "enable_forecast_updates": False
        }
    
    return {
        "microgrid_id": prefs.microgrid_id,
        "phone_number": prefs.phone_number,
        "email": prefs.email,
        "enable_sms": prefs.enable_sms,
        "enable_email": prefs.enable_email,
        "enable_critical_alerts": prefs.enable_critical_alerts,
        "enable_warning_alerts": prefs.enable_warning_alerts,
        "enable_info_alerts": prefs.enable_info_alerts,
        "enable_forecast_updates": prefs.enable_forecast_updates
    }


@router.post("/preferences/{microgrid_id}")
async def update_notification_preferences(
    microgrid_id: str,
    preferences: NotificationPreferenceRequest,
    db: Session = Depends(get_db)
):
    """Update notification preferences for a microgrid"""
    # Verify microgrid exists
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.microgrid_id == microgrid_id
    ).first()
    
    if not prefs:
        prefs = NotificationPreference(
            microgrid_id=microgrid_id,
            phone_number=preferences.phone_number,
            email=preferences.email,
            enable_sms=preferences.enable_sms,
            enable_email=preferences.enable_email,
            enable_critical_alerts=preferences.enable_critical_alerts,
            enable_warning_alerts=preferences.enable_warning_alerts,
            enable_info_alerts=preferences.enable_info_alerts,
            enable_forecast_updates=preferences.enable_forecast_updates
        )
        db.add(prefs)
    else:
        prefs.phone_number = preferences.phone_number
        prefs.email = preferences.email
        prefs.enable_sms = preferences.enable_sms
        prefs.enable_email = preferences.enable_email
        prefs.enable_critical_alerts = preferences.enable_critical_alerts
        prefs.enable_warning_alerts = preferences.enable_warning_alerts
        prefs.enable_info_alerts = preferences.enable_info_alerts
        prefs.enable_forecast_updates = preferences.enable_forecast_updates
    
    db.commit()
    
    return {"status": "success", "preferences": {
        "microgrid_id": prefs.microgrid_id,
        "phone_number": prefs.phone_number,
        "email": prefs.email,
        "enable_sms": prefs.enable_sms,
        "enable_email": prefs.enable_email,
        "enable_critical_alerts": prefs.enable_critical_alerts,
        "enable_warning_alerts": prefs.enable_warning_alerts,
        "enable_info_alerts": prefs.enable_info_alerts,
        "enable_forecast_updates": prefs.enable_forecast_updates
    }}


@router.post("/send-test/{microgrid_id}")
async def send_test_notification(
    microgrid_id: str,
    db: Session = Depends(get_db)
):
    """Send a test SMS notification"""
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.microgrid_id == microgrid_id
    ).first()
    
    if not prefs or not prefs.phone_number:
        raise HTTPException(
            status_code=400,
            detail="No phone number configured for this microgrid"
        )
    
    result = notification_service.send_sms(
        to_number=prefs.phone_number,
        message="🧪 Test notification from SuryaDrishti. Your notification system is working correctly!",
        microgrid_id=microgrid_id
    )
    
    return result

