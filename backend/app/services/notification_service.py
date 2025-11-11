"""
Notification Service for SMS and Push Notifications
Supports Twilio SMS and web push notifications
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Try to import Twilio
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. SMS notifications will be disabled.")


class NotificationService:
    """Service for sending SMS and push notifications"""
    
    def __init__(self):
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_from_number = os.getenv('TWILIO_FROM_NUMBER', '')
        
        self.twilio_client = None
        if TWILIO_AVAILABLE and self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.twilio_client = None
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        microgrid_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send SMS notification via Twilio.
        
        Args:
            to_number: Phone number in E.164 format (e.g., +919876543210)
            message: Message text (max 1600 characters)
            microgrid_id: Optional microgrid ID for logging
        
        Returns:
            Dict with status and message_id if successful
        """
        if not self.twilio_client:
            logger.warning("Twilio not configured. SMS not sent.")
            return {
                'status': 'error',
                'error': 'Twilio not configured',
                'message': 'SMS service not available'
            }
        
        if not self.twilio_from_number:
            logger.warning("Twilio FROM number not configured")
            return {
                'status': 'error',
                'error': 'Twilio FROM number not configured',
                'message': 'SMS service not configured'
            }
        
        try:
            # Truncate message if too long (SMS limit is 1600 chars)
            if len(message) > 1600:
                message = message[:1597] + "..."
            
            logger.info(f"Sending SMS to {to_number} for microgrid {microgrid_id}")
            
            twilio_message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully. SID: {twilio_message.sid}")
            
            return {
                'status': 'success',
                'message_id': twilio_message.sid,
                'to': to_number,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to send SMS'
            }
    
    def send_alert_notification(
        self,
        phone_number: str,
        alert_type: str,
        message: str,
        microgrid_id: str,
        severity: str = 'warning'
    ) -> Dict[str, any]:
        """
        Send alert notification via SMS.
        
        Args:
            phone_number: Phone number in E.164 format
            alert_type: Type of alert (e.g., 'power_drop', 'low_battery', 'cloud_approaching')
            message: Alert message
            microgrid_id: Microgrid ID
            severity: Alert severity ('info', 'warning', 'critical')
        
        Returns:
            Dict with status
        """
        # Format message for SMS
        emoji_map = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        emoji = emoji_map.get(severity, '⚠️')
        
        sms_message = f"{emoji} SuryaDrishti Alert\n\n{message}\n\nMicrogrid: {microgrid_id}\nTime: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_sms(
            to_number=phone_number,
            message=sms_message,
            microgrid_id=microgrid_id
        )
    
    def send_forecast_notification(
        self,
        phone_number: str,
        forecast_summary: Dict,
        microgrid_id: str
    ) -> Dict[str, any]:
        """
        Send forecast summary notification.
        
        Args:
            phone_number: Phone number in E.164 format
            forecast_summary: Dict with forecast summary (e.g., {'next_drop_time': '10:30', 'drop_percent': 25})
            microgrid_id: Microgrid ID
        
        Returns:
            Dict with status
        """
        message_parts = ["📊 Solar Forecast Update"]
        
        if 'next_drop_time' in forecast_summary:
            message_parts.append(f"Power drop expected at {forecast_summary['next_drop_time']}")
            if 'drop_percent' in forecast_summary:
                message_parts.append(f"Expected drop: {forecast_summary['drop_percent']:.0f}%")
        
        if 'battery_action' in forecast_summary:
            message_parts.append(f"Action: {forecast_summary['battery_action']}")
        
        message = "\n".join(message_parts)
        message += f"\n\nMicrogrid: {microgrid_id}"
        
        return self.send_sms(
            to_number=phone_number,
            message=message,
            microgrid_id=microgrid_id
        )
    
    def send_bulk_notifications(
        self,
        phone_numbers: List[str],
        message: str,
        microgrid_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send SMS to multiple recipients.
        
        Args:
            phone_numbers: List of phone numbers
            message: Message text
            microgrid_id: Optional microgrid ID
        
        Returns:
            Dict with results for each recipient
        """
        results = []
        for phone_number in phone_numbers:
            result = self.send_sms(phone_number, message, microgrid_id)
            results.append({
                'phone_number': phone_number,
                **result
            })
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return {
            'status': 'completed',
            'total': len(phone_numbers),
            'success': success_count,
            'failed': len(phone_numbers) - success_count,
            'results': results
        }


# Global instance
notification_service = NotificationService()











