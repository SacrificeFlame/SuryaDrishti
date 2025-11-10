"""
Irrigation Pump Delay Automation Service
Automatically delays irrigation pumps when power drops are forecasted
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.database import Device, Alert
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class IrrigationAutomation:
    """Service for automating irrigation pump delays based on forecasts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_delay_pumps(
        self,
        microgrid_id: str,
        forecast_data: List[Dict[str, Any]],
        current_soc: float,
        battery_capacity_kwh: float
    ) -> Dict[str, Any]:
        """
        Check forecast for power drops and delay irrigation pumps if needed.
        
        Args:
            microgrid_id: Microgrid ID
            forecast_data: List of forecast points with power predictions
            current_soc: Current battery state of charge (0-1)
            battery_capacity_kwh: Battery capacity in kWh
        
        Returns:
            Dict with action taken and delayed devices
        """
        # Get irrigation pumps for this microgrid
        irrigation_pumps = self.db.query(Device).filter(
            Device.microgrid_id == microgrid_id,
            Device.is_active == True
        ).filter(
            (Device.device_type == 'irrigation') |
            (Device.name.ilike('%irrigation%')) |
            (Device.name.ilike('%pump%'))
        ).all()
        
        if not irrigation_pumps:
            return {
                'action': 'none',
                'reason': 'No irrigation pumps found',
                'delayed_devices': []
            }
        
        # Analyze forecast for power drops in next 30-60 minutes
        now = datetime.utcnow()
        power_drops = []
        
        for point in forecast_data[:12]:  # Check next 12 hours (hourly forecast)
            timestamp_str = point.get('timestamp')
            if isinstance(timestamp_str, str):
                try:
                    point_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    continue
            else:
                continue
            
            # Check if within next 60 minutes
            time_diff = (point_time - now).total_seconds() / 60.0
            if 30 <= time_diff <= 60:  # 30-60 minutes ahead
                power_data = point.get('power_kw', {})
                if isinstance(power_data, dict):
                    forecast_power = power_data.get('mean', 0)
                    
                    # Get current power (first forecast point)
                    if forecast_data:
                        current_power_data = forecast_data[0].get('power_kw', {})
                        if isinstance(current_power_data, dict):
                            current_power = current_power_data.get('mean', 0)
                            
                            # Detect significant drop (>25%)
                            if current_power > 0 and forecast_power < (current_power * 0.75):
                                drop_percent = ((current_power - forecast_power) / current_power) * 100
                                power_drops.append({
                                    'time': point_time.isoformat(),
                                    'forecast_power': forecast_power,
                                    'current_power': current_power,
                                    'drop_percent': drop_percent
                                })
        
        # Decision logic: Delay pumps if:
        # 1. Power drop > 25% is forecasted in next 30-60 min
        # 2. Battery SOC < 40% (low battery buffer)
        # 3. Or power drop > 40% regardless of SOC
        
        should_delay = False
        reason = None
        
        if power_drops:
            max_drop = max(p['drop_percent'] for p in power_drops)
            
            if max_drop > 40:  # Severe drop (>40%)
                should_delay = True
                reason = f"Severe power drop forecasted ({max_drop:.0f}%)"
            elif max_drop > 25 and current_soc < 0.4:  # Moderate drop with low battery
                should_delay = True
                reason = f"Power drop forecasted ({max_drop:.0f}%) with low battery ({current_soc*100:.0f}%)"
        
        if not should_delay:
            return {
                'action': 'none',
                'reason': 'No delay needed',
                'delayed_devices': [],
                'power_drops': power_drops
            }
        
        # Delay irrigation pumps
        delayed_devices = []
        for pump in irrigation_pumps:
            # Mark device as temporarily disabled (you might want a separate 'delayed_until' field)
            # For now, we'll create an alert
            alert = Alert(
                microgrid_id=microgrid_id,
                timestamp=datetime.utcnow(),
                severity='warning',
                message=f"Irrigation pump '{pump.name}' delayed due to forecasted power drop. {reason}",
                action_taken=f"Pump {pump.name} delayed until power stabilizes"
            )
            self.db.add(alert)
            
            delayed_devices.append({
                'device_id': pump.id,
                'device_name': pump.name,
                'reason': reason
            })
        
        self.db.commit()
        
        logger.info(f"Delayed {len(delayed_devices)} irrigation pumps for microgrid {microgrid_id}: {reason}")
        
        return {
            'action': 'delayed',
            'reason': reason,
            'delayed_devices': delayed_devices,
            'power_drops': power_drops,
            'current_soc': current_soc,
            'battery_capacity_kwh': battery_capacity_kwh
        }








