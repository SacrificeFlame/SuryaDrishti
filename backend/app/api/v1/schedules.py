"""
Schedule Management API endpoints
Handles schedule generation and retrieval.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.database import Schedule, Microgrid, Device, SystemConfiguration
from app.models.schemas import (
    ScheduleResponse,
    ScheduleGenerateRequest,
    OptimizationMetrics
)
from app.services.scheduler_engine import SchedulerEngine
import logging
from dateutil import parser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/microgrid/{microgrid_id}/schedules/generate", response_model=ScheduleResponse, status_code=201)
async def generate_schedule(
    microgrid_id: str,
    request: ScheduleGenerateRequest,
    db: Session = Depends(get_db)
):
    """Generate an optimized schedule for a microgrid."""
    # Verify microgrid exists
    microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
    if not microgrid:
        raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
    
    # Get system configuration
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
            generator_fuel_consumption_l_per_kwh=0.25,
            generator_fuel_cost_per_liter=80.0,
            generator_min_runtime_minutes=30,
            generator_max_power_kw=20.0,
            optimization_mode=request.optimization_mode or 'cost',
            safety_margin_critical_loads=0.1
        )
        db.add(config)
        db.commit()
    
    # Get devices
    devices = db.query(Device).filter(
        Device.microgrid_id == microgrid_id,
        Device.is_active == True
    ).all()
    
    if not devices:
        raise HTTPException(
            status_code=400,
            detail="No active devices found. Please add devices first."
        )
    
    # Get forecast data - use external API
    forecast_data = []
    if request.use_forecast:
        try:
            from app.services.external_forecast_service import (
                fetch_forecast_from_external_api,
                parse_external_api_response,
                convert_to_microgrid_forecast_format
            )
            
            logger.info(f"Fetching forecast for microgrid {microgrid_id} from external API...")
            
            # Fetch from external API
            external_data = await fetch_forecast_from_external_api(source="hybrid")
            logger.info("Successfully fetched data from external API for scheduler")
            
            # Parse the response
            parsed_forecast = parse_external_api_response(external_data)
            
            # Convert to microgrid format
            forecast_result = convert_to_microgrid_forecast_format(
                parsed_forecast,
                microgrid_id,
                microgrid.latitude,
                microgrid.longitude,
                microgrid.capacity_kw
            )
            
            logger.info("Successfully converted external API forecast for scheduler")
            
            if forecast_result and 'forecast' in forecast_result:
                # Convert the forecast format to scheduler format
                forecast_points = forecast_result['forecast']
                
                if not forecast_points or len(forecast_points) == 0:
                    raise ValueError("Forecast API returned empty forecast data")
                
                # Convert hourly forecast to 10-minute intervals for scheduler
                from datetime import timedelta
                for point in forecast_points:
                    # Parse timestamp - handle both string and datetime objects
                    point_timestamp = point.get('timestamp')
                    if isinstance(point_timestamp, str):
                        # Try parsing ISO format
                        try:
                            point_time = datetime.fromisoformat(point_timestamp.replace('Z', '+00:00'))
                        except:
                            # Try parsing other formats
                            point_time = parser.parse(point_timestamp)
                    elif isinstance(point_timestamp, datetime):
                        point_time = point_timestamp
                    else:
                        logger.warning(f"Unexpected timestamp format: {point_timestamp}, skipping point")
                        continue
                    
                    # Get power and GHI values
                    power_data = point.get('power_kw', {})
                    if isinstance(power_data, dict):
                        power_mean = power_data.get('mean', 0)
                        power_p10 = power_data.get('p10', power_mean * 0.8)
                        power_p90 = power_data.get('p90', power_mean * 1.2)
                    else:
                        power_mean = float(power_data) if power_data else 0
                        power_p10 = power_mean * 0.8
                        power_p90 = power_mean * 1.2
                    
                    ghi_data = point.get('ghi', {})
                    if isinstance(ghi_data, dict):
                        ghi_mean = ghi_data.get('mean', 0)
                        ghi_p10 = ghi_data.get('p10', ghi_mean * 0.8)
                        ghi_p90 = ghi_data.get('p90', ghi_mean * 1.2)
                    else:
                        ghi_mean = float(ghi_data) if ghi_data else 0
                        ghi_p10 = ghi_mean * 0.8
                        ghi_p90 = ghi_mean * 1.2
                    
                    solar_elevation = point.get('solar_elevation', 0)
                    is_daytime = point.get('is_daytime', False)
                    
                    # Create 6 time slots for this hour (10-minute intervals)
                    for minute_offset in [0, 10, 20, 30, 40, 50]:
                        slot_time = point_time + timedelta(minutes=minute_offset)
                        forecast_data.append({
                            'timestamp': slot_time.isoformat(),
                            'power_kw': {
                                'mean': power_mean,
                                'p10': power_p10,
                                'p90': power_p90
                            },
                            'ghi': {
                                'mean': ghi_mean,
                                'p10': ghi_p10,
                                'p90': ghi_p90
                            },
                            'solar_elevation': solar_elevation,
                            'is_daytime': is_daytime
                        })
                
                logger.info(f"Successfully fetched {len(forecast_points)} hourly forecast points, expanded to {len(forecast_data)} 10-minute intervals")
            else:
                raise ValueError("Forecast API returned empty or invalid data (missing 'forecast' key)")
                
        except Exception as e:
            # If forecast fails, try internal forecast
            logger.error(f"Forecast fetch failed: {e}", exc_info=True)
            logger.warning("Trying internal NGBoost forecast as fallback...")
            
            try:
                from app.api.v1.forecast_microgrid import get_microgrid_forecast
                # Get internal forecast
                internal_forecast = await get_microgrid_forecast(
                    microgrid_id=microgrid_id,
                    horizon_hours=24,
                    training_days=180,
                    retrain=False,
                    db=db
                )
                
                # Expand hourly to 10-minute intervals
                from datetime import timedelta
                forecast_points = internal_forecast.get('forecast', [])
                for point in forecast_points:
                    # Each hourly point becomes 6 x 10-minute intervals
                    base_timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                    if base_timestamp.tzinfo:
                        base_timestamp = base_timestamp.replace(tzinfo=None)
                    
                    for interval in range(6):
                        timestamp = base_timestamp + timedelta(minutes=interval * 10)
                        power_mean = point.get('power_kw', {}).get('mean', 0) / 6.0  # Distribute hourly power
                        ghi_mean = point.get('ghi', {}).get('mean', 0) / 6.0
                        
                        forecast_data.append({
                            'timestamp': timestamp.isoformat(),
                            'power_kw': {
                                'mean': power_mean,
                                'p10': power_mean * 0.8,
                                'p90': power_mean * 1.2
                            },
                            'ghi': {
                                'mean': ghi_mean,
                                'p10': ghi_mean * 0.8,
                                'p90': ghi_mean * 1.2
                            },
                            'solar_elevation': point.get('solar_elevation', 0),
                            'is_daytime': point.get('is_daytime', False)
                        })
                
                logger.info(f"Successfully used internal forecast: {len(forecast_data)} points")
            except Exception as internal_error:
                logger.error(f"Internal forecast also failed: {internal_error}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate forecast. External API error: {str(e)[:100]}, Internal error: {str(internal_error)[:100]}"
                )
    else:
        # If use_forecast is False, still get real forecast data (don't generate fake data)
        logger.warning("use_forecast=False, but generating schedule requires forecast data. Using internal forecast.")
        try:
            from app.api.v1.forecast_microgrid import get_microgrid_forecast
            internal_forecast = await get_microgrid_forecast(
                microgrid_id=microgrid_id,
                horizon_hours=24,
                training_days=180,
                retrain=False,
                db=db
            )
            
            # Expand hourly to 10-minute intervals
            from datetime import timedelta
            forecast_points = internal_forecast.get('forecast', [])
            for point in forecast_points:
                base_timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                if base_timestamp.tzinfo:
                    base_timestamp = base_timestamp.replace(tzinfo=None)
                
                for interval in range(6):
                    timestamp = base_timestamp + timedelta(minutes=interval * 10)
                    power_mean = point.get('power_kw', {}).get('mean', 0) / 6.0
                    ghi_mean = point.get('ghi', {}).get('mean', 0) / 6.0
                    
                    forecast_data.append({
                        'timestamp': timestamp.isoformat(),
                        'power_kw': {'mean': power_mean},
                        'ghi': {'mean': ghi_mean},
                        'solar_elevation': point.get('solar_elevation', 0),
                        'is_daytime': point.get('is_daytime', False)
                    })
            
            logger.info(f"Generated forecast from internal model: {len(forecast_data)} points")
        except Exception as forecast_error:
            logger.error(f"Failed to get internal forecast: {forecast_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Schedule generation requires forecast data, but forecast generation failed: {str(forecast_error)[:200]}"
            )
    
    # Convert devices to dict format
    devices_dict = [
        {
            'id': d.id,
            'name': d.name,
            'power_consumption_watts': d.power_consumption_watts,
            'device_type': d.device_type,
            'minimum_runtime_minutes': d.minimum_runtime_minutes,
            'preferred_hours': d.preferred_hours,
            'priority_level': d.priority_level,
            'is_active': d.is_active
        }
        for d in devices
    ]
    
    # Get current battery SOC from system status (default to 50%)
    initial_soc = 0.5  # TODO: Get from actual system status
    
    # Convert config to dict
    config_dict = {
        'capacity_kw': microgrid.capacity_kw,  # Solar panel capacity for high solar detection
        'battery_capacity_kwh': config.battery_capacity_kwh,
        'battery_max_charge_rate_kw': config.battery_max_charge_rate_kw,
        'battery_max_discharge_rate_kw': config.battery_max_discharge_rate_kw,
        'battery_efficiency': config.battery_efficiency,
        'battery_min_soc': config.battery_min_soc,
        'battery_max_soc': config.battery_max_soc,
        'grid_peak_rate_per_kwh': config.grid_peak_rate_per_kwh,
        'grid_off_peak_rate_per_kwh': config.grid_off_peak_rate_per_kwh,
        'grid_peak_hours': config.grid_peak_hours or {'start': 8, 'end': 20},
        'grid_export_rate_per_kwh': getattr(config, 'grid_export_rate_per_kwh', 4.0),
        'grid_export_enabled': getattr(config, 'grid_export_enabled', True),
        'generator_fuel_consumption_l_per_kwh': config.generator_fuel_consumption_l_per_kwh,
        'generator_fuel_cost_per_liter': config.generator_fuel_cost_per_liter,
        'generator_min_runtime_minutes': config.generator_min_runtime_minutes,
        'generator_max_power_kw': config.generator_max_power_kw,
        'optimization_mode': request.optimization_mode or config.optimization_mode,
        'safety_margin_critical_loads': config.safety_margin_critical_loads
    }
    
    # Generate schedule
    scheduler = SchedulerEngine(config_dict)
    schedule_result = scheduler.generate_schedule(
        forecast_data=forecast_data,
        devices=devices_dict,
        initial_battery_soc=initial_soc,
        time_slot_minutes=10
    )
    
    # Determine schedule date
    schedule_date = request.date or datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if schedule already exists for this date
    existing_schedule = db.query(Schedule).filter(
        Schedule.microgrid_id == microgrid_id,
        Schedule.date == schedule_date
    ).first()
    
    if existing_schedule:
        # Update existing schedule
        existing_schedule.schedule_data = schedule_result
        existing_schedule.optimization_metrics = schedule_result.get('metrics', {})
        existing_schedule.is_active = True
        existing_schedule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_schedule)
        return existing_schedule
    else:
        # Create new schedule
        db_schedule = Schedule(
            microgrid_id=microgrid_id,
            date=schedule_date,
            schedule_data=schedule_result,
            optimization_metrics=schedule_result.get('metrics', {}),
            is_active=True
        )
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule


@router.get("/microgrid/{microgrid_id}/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    microgrid_id: str,
    date: Optional[date] = Query(None, description="Get schedule for specific date"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get schedules for a microgrid."""
    query = db.query(Schedule).filter(Schedule.microgrid_id == microgrid_id)
    
    if date:
        query = query.filter(Schedule.date == datetime.combine(date, datetime.min.time()))
    
    schedules = query.order_by(Schedule.date.desc()).limit(limit).all()
    return schedules


@router.get("/microgrid/{microgrid_id}/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    microgrid_id: str,
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific schedule."""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.microgrid_id == microgrid_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule


@router.delete("/microgrid/{microgrid_id}/schedules/{schedule_id}", status_code=204)
async def delete_schedule(
    microgrid_id: str,
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a schedule."""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.microgrid_id == microgrid_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    
    return None

