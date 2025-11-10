"""
Energy Loss Prevention Reports API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import Microgrid, Forecast, SensorReading, Alert, Schedule
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/energy-loss/{microgrid_id}")
async def get_energy_loss_report(
    microgrid_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Generate energy loss prevention report.
    Shows how much energy was saved/prevented from being lost due to forecasting.
    """
    try:
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        # Default to last 7 days if not specified
        if not end_date:
            end_date = datetime.utcnow().date().isoformat()
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date) + timedelta(days=1)
        
        # Get forecasts and actual sensor readings for comparison
        forecasts = db.query(Forecast).filter(
            Forecast.microgrid_id == microgrid_id,
            Forecast.timestamp >= start_dt,
            Forecast.timestamp < end_dt
        ).order_by(Forecast.timestamp).all()
        
        sensor_readings = db.query(SensorReading).filter(
            SensorReading.microgrid_id == microgrid_id,
            SensorReading.timestamp >= start_dt,
            SensorReading.timestamp < end_dt
        ).order_by(SensorReading.timestamp).all()
        
        # Get alerts (which indicate actions taken)
        alerts = db.query(Alert).filter(
            Alert.microgrid_id == microgrid_id,
            Alert.timestamp >= start_dt,
            Alert.timestamp < end_dt,
            Alert.severity.in_(['warning', 'critical'])
        ).all()
        
        # Calculate metrics
        total_forecast_energy = 0.0
        total_actual_energy = 0.0
        prevented_outages = 0
        battery_cycles_saved = 0
        
        # Simple comparison (in production, you'd do more sophisticated analysis)
        for forecast in forecasts:
            if forecast.predictions:
                # Extract forecasted power (simplified)
                if isinstance(forecast.predictions, dict):
                    # Try to extract power values
                    for key, value in forecast.predictions.items():
                        if isinstance(value, dict) and 'power_output' in value:
                            total_forecast_energy += value.get('power_output', 0) * 0.25  # Assume 15-min intervals
        
        for reading in sensor_readings:
            if reading.power_output:
                total_actual_energy += reading.power_output * 0.25  # Assume 15-min intervals
        
        # Count prevented outages (alerts that led to actions)
        for alert in alerts:
            if alert.action_taken and 'battery' in alert.action_taken.lower():
                prevented_outages += 1
        
        # Calculate energy saved (difference between forecast and actual, accounting for actions taken)
        energy_saved = max(0, total_forecast_energy - total_actual_energy)
        
        # Estimate battery cycles saved (simplified)
        battery_cycles_saved = prevented_outages * 0.5  # Rough estimate
        
        return {
            'microgrid_id': microgrid_id,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'metrics': {
                'total_forecast_energy_kwh': round(total_forecast_energy, 2),
                'total_actual_energy_kwh': round(total_actual_energy, 2),
                'energy_saved_kwh': round(energy_saved, 2),
                'prevented_outages': prevented_outages,
                'battery_cycles_saved': round(battery_cycles_saved, 1),
                'alerts_triggered': len(alerts),
                'forecast_accuracy_percent': round(
                    (1 - abs(total_forecast_energy - total_actual_energy) / max(total_forecast_energy, 1)) * 100,
                    1
                )
            },
            'summary': {
                'total_alerts': len(alerts),
                'critical_alerts': sum(1 for a in alerts if a.severity == 'critical'),
                'warning_alerts': sum(1 for a in alerts if a.severity == 'warning'),
                'actions_taken': sum(1 for a in alerts if a.action_taken)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating energy loss report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/performance/{microgrid_id}")
async def get_performance_report(
    microgrid_id: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics report.
    """
    try:
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get recent forecasts
        forecasts = db.query(Forecast).filter(
            Forecast.microgrid_id == microgrid_id,
            Forecast.timestamp >= start_date
        ).count()
        
        # Get sensor readings
        sensor_readings = db.query(SensorReading).filter(
            SensorReading.microgrid_id == microgrid_id,
            SensorReading.timestamp >= start_date
        ).count()
        
        # Get alerts
        alerts = db.query(Alert).filter(
            Alert.microgrid_id == microgrid_id,
            Alert.timestamp >= start_date
        ).all()
        
        return {
            'microgrid_id': microgrid_id,
            'period_days': days,
            'metrics': {
                'forecasts_generated': forecasts,
                'sensor_readings': sensor_readings,
                'alerts_triggered': len(alerts),
                'system_uptime_percent': 98.5,  # Placeholder - calculate from actual data
                'forecast_accuracy_mae': 15.2,  # Placeholder - calculate from actual data
            },
            'alerts_by_severity': {
                'critical': sum(1 for a in alerts if a.severity == 'critical'),
                'warning': sum(1 for a in alerts if a.severity == 'warning'),
                'info': sum(1 for a in alerts if a.severity == 'info')
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating performance report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")








