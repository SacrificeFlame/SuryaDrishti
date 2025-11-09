from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
import httpx
import logging
from typing import Optional, Dict
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from app.core.database import get_db
from app.api.v1.forecast_microgrid import ghi_to_power

router = APIRouter()
logger = logging.getLogger(__name__)

# External API configuration
EXTERNAL_API_URL = "http://127.0.0.1:8000/api/run"
EXTERNAL_API_KEY = "aryan1234%^&*()"

async def fetch_external_forecast_api(source: str = "hybrid", timeout: float = 30.0) -> Dict:
    """
    Fetch forecast data from external API.
    
    Args:
        source: Forecast source type (default: "hybrid")
        timeout: Request timeout in seconds (default: 30.0)
    
    Returns:
        Dictionary with forecast data
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": EXTERNAL_API_KEY,
            }
            
            payload = {"source": source}
            
            logger.info(f"Calling external forecast API: {EXTERNAL_API_URL} with source={source}")
            response = await client.post(
                EXTERNAL_API_URL,
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"External API returned status {response.status_code}, data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            return data
            
    except httpx.TimeoutException:
        logger.error(f"External forecast API timeout after {timeout}s")
        raise Exception(f"External API timeout after {timeout} seconds")
    except httpx.HTTPStatusError as e:
        logger.error(f"External forecast API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        raise Exception(f"External API returned status {e.response.status_code}")
    except Exception as e:
        logger.error(f"Error calling external forecast API: {e}")
        raise

# REMOVED: generate_mock_forecast_data - NO MOCK DATA ALLOWED

@router.options("/schedule")
async def options_schedule():
    """Handle CORS preflight requests"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/schedule")
async def get_forecast_schedule(
    forecast_hours: int = Query(12, ge=1, le=48, description="Forecast horizon in hours"),
    microgrid_id: str = Query("microgrid_001", description="Microgrid ID to use for forecast"),
    db: Session = Depends(get_db)
):
    """
    Get forecast schedule using the external forecast API.
    Uses the external API at /api/run with source="hybrid".
    
    Returns forecast data in schedule format for the dashboard.
    """
    try:
        logger.info(f"Fetching forecast schedule for microgrid {microgrid_id} (forecast_hours={forecast_hours})")
        
        # Get microgrid info
        from app.models.database import Microgrid
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            logger.warning(f"Microgrid {microgrid_id} not found, using defaults")
            capacity_kw = 50.0
            location = {'lat': 28.4595, 'lon': 77.0266}
        else:
            capacity_kw = microgrid.capacity_kw
            location = {'lat': microgrid.latitude, 'lon': microgrid.longitude}
        
        # Fetch from external API
        try:
            from app.services.external_forecast_service import (
                fetch_forecast_from_external_api,
                parse_external_api_response,
                convert_to_microgrid_forecast_format
            )
            
            external_data = await fetch_forecast_from_external_api(source="hybrid")
            logger.info("Successfully fetched data from external API for schedule")
            
            # Parse the response
            parsed_forecast = parse_external_api_response(external_data)
            
            # Convert to microgrid format first
            microgrid_forecast = convert_to_microgrid_forecast_format(
                parsed_forecast,
                microgrid_id,
                location['lat'],
                location['lon'],
                capacity_kw
            )
            
            # Limit to requested horizon
            forecast_points = microgrid_forecast['forecast'][:forecast_hours]
            
            # Get source from metadata
            source = microgrid_forecast.get('metadata', {}).get('data_source', 'external_api_hybrid')
            
        except Exception as e:
            logger.error(f"External API call failed: {e}", exc_info=True)
            logger.warning("External API unavailable. Falling back to internal forecast via microgrid endpoint.")
            
            # Fall back to internal forecast by calling the microgrid forecast endpoint
            try:
                from app.api.v1.forecast_microgrid import get_microgrid_forecast
                # Call the internal forecast endpoint
                microgrid_forecast = await get_microgrid_forecast(
                    microgrid_id=microgrid_id,
                    horizon_hours=forecast_hours,
                    training_days=180,
                    retrain=False,
                    db=db
                )
                
                # Convert microgrid forecast to schedule format
                schedule = []
                forecast_kW = []
                weather = []
                
                now = datetime.utcnow()
                initial_soc = 50.0
                ist_tz = pytz.timezone('Asia/Kolkata')
                
                for idx, point in enumerate(microgrid_forecast.get('forecast', [])[:forecast_hours]):
                    point_timestamp = point.get('timestamp')
                    if isinstance(point_timestamp, str):
                        try:
                            point_time = datetime.fromisoformat(point_timestamp.replace('Z', '+00:00'))
                        except:
                            point_time = now + timedelta(hours=idx)
                    else:
                        point_time = now + timedelta(hours=idx)
                    
                    if point_time.tzinfo is None:
                        point_time_utc = pytz.utc.localize(point_time)
                    else:
                        point_time_utc = point_time
                    point_time_ist = point_time_utc.astimezone(ist_tz)
                    
                    power_data = point.get('power_kw', {})
                    if isinstance(power_data, dict):
                        solar_kW = power_data.get('mean', 0)
                    else:
                        solar_kW = float(power_data) if power_data else 0
                    
                    ghi_data = point.get('ghi', {})
                    if isinstance(ghi_data, dict):
                        ghi = ghi_data.get('mean', 0)
                    else:
                        ghi = float(ghi_data) if ghi_data else 0
                    
                    load_kW = 15.0 + (idx % 3) * 2
                    net_energy = solar_kW - load_kW
                    if net_energy > 0:
                        charging_kW = min(net_energy, 10.0)
                        discharging_kW = 0
                    else:
                        charging_kW = 0
                        discharging_kW = min(abs(net_energy), 10.0)
                    
                    soc_change = (charging_kW * 0.95 - discharging_kW / 0.95) / 50.0
                    initial_soc = max(20, min(95, initial_soc + soc_change))
                    
                    schedule.append({
                        'step': idx + 1,
                        'time': point_time_ist.strftime('%Y-%m-%d %H:%M:%S'),
                        'solar_kW': round(solar_kW, 2),
                        'load_kW': round(load_kW, 2),
                        'charging_kW': round(charging_kW, 2),
                        'discharging_kW': round(discharging_kW, 2),
                        'soc_percent': round(initial_soc, 1),
                    })
                    
                    forecast_kW.append(round(solar_kW, 2))
                    
                    weather.append({
                        'time': point_time_ist.strftime('%Y-%m-%d %H:%M:%S'),
                        'ghi': round(ghi, 1),
                        'cloud': 0,
                        'poa_global': round(ghi, 1),
                        'predicted_kW': round(solar_kW, 2),
                    })
                
                source = microgrid_forecast.get('metadata', {}).get('data_source', 'internal_ngboost')
                if source == 'internal_ngboost_fallback':
                    source = 'internal_ngboost (external API unavailable)'
                
                response_data = {
                    'status': 'ok',
                    'data': {
                        'meta': {
                            'generated_at': datetime.utcnow().isoformat(),
                            'location': location,
                            'forecast_horizon_hours': forecast_hours,
                            'source': source,
                        },
                        'schedule': schedule,
                        'soc_target': 0.8,
                        'forecast_kW': forecast_kW,
                        'weather': weather,
                    }
                }
                
                logger.info(f"Successfully generated schedule from internal forecast: {len(schedule)} items")
                return JSONResponse(
                    content=response_data,
                    headers={"Access-Control-Allow-Origin": "*"}
                )
                
            except Exception as internal_error:
                logger.error(f"Internal forecast also failed: {internal_error}", exc_info=True)
                logger.error(f"All forecast methods failed: {internal_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"All forecast methods failed. External API: {str(e)[:100]}, Internal: {str(internal_error)[:100]}"
                )
        
        # Use proper scheduler engine for battery operations
        from app.services.scheduler_engine import SchedulerEngine
        from app.models.database import Device, SystemConfiguration
        
        # Get microgrid configuration for battery parameters
        config = db.query(SystemConfiguration).filter(
            SystemConfiguration.microgrid_id == microgrid_id
        ).first()
        
        # Get battery parameters from config or use defaults
        battery_capacity_kwh = config.battery_capacity_kwh if config else 50.0
        battery_max_charge_kw = config.battery_max_charge_rate_kw if config else 10.0
        battery_max_discharge_kw = config.battery_max_discharge_rate_kw if config else 10.0
        battery_efficiency = config.battery_efficiency if config else 0.95
        battery_min_soc = config.battery_min_soc if config else 0.2
        battery_max_soc = config.battery_max_soc if config else 0.95
        
        # Get devices for load calculation
        devices = db.query(Device).filter(Device.microgrid_id == microgrid_id).all()
        device_list = []
        for device in devices:
            # Parse preferred_hours from JSON if available
            preferred_hours = None
            if device.preferred_hours:
                if isinstance(device.preferred_hours, dict):
                    preferred_hours = device.preferred_hours
                elif isinstance(device.preferred_hours, str):
                    import json
                    try:
                        preferred_hours = json.loads(device.preferred_hours)
                    except:
                        preferred_hours = None
            
            device_list.append({
                'id': device.id,
                'name': device.name,
                'device_type': device.device_type or 'flexible',
                'power_consumption_watts': device.power_consumption_watts or 0,
                'is_active': device.is_active if device.is_active is not None else True,
                'preferred_hours': preferred_hours
            })
        
        # If no devices, create default essential load
        if not device_list:
            device_list = [{
                'id': 'default_load',
                'name': 'Essential Load',
                'device_type': 'essential',
                'power_consumption_watts': 15000,  # 15 kW default
                'is_active': True,
                'preferred_hours': None
            }]
        
        # Prepare forecast data for scheduler
        forecast_data_for_scheduler = []
        now = datetime.utcnow()
        ist_tz = pytz.timezone('Asia/Kolkata')
        
        for idx, point in enumerate(forecast_points):
            point_timestamp = point.get('timestamp')
            if isinstance(point_timestamp, str):
                try:
                    point_time = datetime.fromisoformat(point_timestamp.replace('Z', '+00:00'))
                except:
                    point_time = now + timedelta(hours=idx)
            else:
                point_time = now + timedelta(hours=idx)
            
            if point_time.tzinfo is None:
                point_time_utc = pytz.utc.localize(point_time)
            else:
                point_time_utc = point_time
            
            power_data = point.get('power_kw', {})
            if isinstance(power_data, dict):
                solar_kW = power_data.get('mean', 0)
            else:
                solar_kW = float(power_data) if power_data else 0
            
            forecast_data_for_scheduler.append({
                'timestamp': point_time_utc.isoformat(),
                'power_kw': {'mean': solar_kW}
            })
        
        # Initialize scheduler engine
        scheduler_config = {
            'battery_capacity_kwh': battery_capacity_kwh,
            'battery_max_charge_rate_kw': battery_max_charge_kw,
            'battery_max_discharge_rate_kw': battery_max_discharge_kw,
            'battery_efficiency': battery_efficiency,
            'battery_min_soc': battery_min_soc,
            'battery_max_soc': battery_max_soc,
            'grid_peak_rate_per_kwh': 10.0,
            'grid_off_peak_rate_per_kwh': 5.0,
            'grid_peak_hours': {'start': 8, 'end': 20},
            'grid_export_rate_per_kwh': 4.0,
            'grid_export_enabled': True,
            'generator_fuel_cost_per_liter': 80.0,
            'generator_fuel_consumption_l_per_kwh': 0.25,
            'generator_max_power_kw': 20.0,
            'generator_min_runtime_minutes': 30,
            'optimization_mode': 'cost',
            'safety_margin': 0.1
        }
        
        scheduler = SchedulerEngine(scheduler_config)
        
        # Get initial SOC from system status or use default
        from app.api.v1.microgrid import get_system_status
        try:
            status_response = await get_system_status(microgrid_id, db)
            # SystemStatus returns battery.soc as a number (0-100), convert to 0-1
            battery_soc = status_response.battery.get('soc', 50) if hasattr(status_response, 'battery') else 50
            initial_soc = battery_soc / 100.0  # Convert percentage to fraction
        except:
            initial_soc = 0.5  # Default 50%
        
        # Generate schedule using scheduler engine
        scheduler_result = scheduler.generate_schedule(
            forecast_data=forecast_data_for_scheduler,
            devices=device_list,
            initial_battery_soc=initial_soc,
            time_slot_minutes=60  # 1 hour slots
        )
        
        # Convert scheduler output to schedule format
        schedule = []
        forecast_kW = []
        weather = []
        
        for idx, slot in enumerate(scheduler_result['schedule']):
            slot_time = datetime.fromisoformat(slot['time'].replace('Z', '+00:00'))
            if slot_time.tzinfo is None:
                slot_time_utc = pytz.utc.localize(slot_time)
            else:
                slot_time_utc = slot_time
            slot_time_ist = slot_time_utc.astimezone(ist_tz)
            
            # Get corresponding forecast point for GHI
            ghi = 0
            if idx < len(forecast_points):
                ghi_data = forecast_points[idx].get('ghi', {})
                if isinstance(ghi_data, dict):
                    ghi = ghi_data.get('mean', 0)
                else:
                    ghi = float(ghi_data) if ghi_data else 0
            
            schedule.append({
                'step': idx + 1,
                'time': slot_time_ist.strftime('%Y-%m-%d %H:%M:%S'),
                'solar_kW': round(slot['solar_generation_kw'], 2),
                'load_kW': round(slot['total_load_kw'], 2),
                'charging_kW': round(slot['battery_charge_kw'], 2),
                'discharging_kW': round(slot['battery_discharge_kw'], 2),
                'soc_percent': round(slot['battery_soc'] * 100, 1),  # Convert to percentage
            })
            
            forecast_kW.append(round(slot['solar_generation_kw'], 2))
            
            weather.append({
                'time': slot_time_ist.strftime('%Y-%m-%d %H:%M:%S'),
                'ghi': round(ghi, 1),
                'cloud': 0,
                'poa_global': round(ghi, 1),
                'predicted_kW': round(slot['solar_generation_kw'], 2),
            })
        
        # Build response
        response_data = {
            'status': 'ok',
            'data': {
                'meta': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'location': location,
                    'forecast_horizon_hours': forecast_hours,
                    'source': source if 'source' in locals() else 'external_api_hybrid',
                },
                'schedule': schedule,
                'soc_target': 0.8,
                'forecast_kW': forecast_kW,
                'weather': weather,
            }
        }
            
        logger.info(f"Successfully generated schedule: {len(schedule)} items")
        
        return JSONResponse(
            content=response_data,
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast schedule: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate forecast schedule: {str(e)[:200]}"
        )


@router.get("/ngboost")
async def get_ngboost_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    horizon_hours: int = Query(24, ge=1, le=48, description="Forecast horizon in hours"),
    retrain: bool = Query(False, description="Retrain model on fresh data"),
    training_days: int = Query(180, ge=30, le=730, description="Days of historical data for training (default 180)")
):
    """
    Get 24-hour ahead GHI forecast using NGBoost probabilistic model.
    Uses Open-Meteo data source and NGBoost for probabilistic predictions.
    
    Returns probabilistic forecasts with P10, P50, P90 quantiles and clear-sky comparison.
    
    Features:
    - Enhanced feature engineering (atmospheric, seasonal, solar geometry)
    - Clear-sky baseline comparison
    - Probabilistic uncertainty estimates
    - Automatic model training/loading
    """
    try:
        from app.services.open_meteo_service import OpenMeteoService
        from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data
        from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel
        
        logger.info(f"Fetching NGBoost forecast for ({lat}, {lon}), horizon={horizon_hours}h, training_days={training_days}")
        
        # Initialize services
        meteo_service = OpenMeteoService()
        
        # Fetch data - use more days for better model performance
        logger.info("Fetching Open-Meteo data...")
        hist_df, fc_df = meteo_service.fetch_combined(
            lat=lat,
            lon=lon,
            past_days=training_days,
            forecast_hours=horizon_hours
        )
        
        # Preprocess data
        logger.info("Preprocessing data...")
        df_processed = preprocess_open_meteo_data(
            hist_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=horizon_hours
        )
        
        # Load or train model
        model_path = Path("data/models/ngboost_24h.joblib")
        feature_path = Path("data/models/ngboost_features.joblib")
        
        if retrain or not model_path.exists():
            logger.info("Training NGBoost model...")
            model = NGBoostIrradianceModel()
            target_col = f"target_{horizon_hours}h"
            model.train(
                df_processed,
                target_col=target_col,
                save_path=str(model_path),
                feature_cols_path=str(feature_path)
            )
        else:
            logger.info("Loading existing NGBoost model...")
            model = NGBoostIrradianceModel(
                model_path=str(model_path),
                feature_cols_path=str(feature_path)
            )
        
        # Preprocess forecast data for prediction
        fc_processed = preprocess_open_meteo_data(
            fc_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=0  # No target for forecast
        )
        
        # Make predictions
        logger.info("Generating predictions...")
        predictions = model.predict(fc_processed, return_uncertainty=True)
        
        # Format response with clear-sky comparison
        forecast_times = fc_processed["time_local"].dt.strftime("%Y-%m-%d %H:%M").tolist()
        
        # Get clear-sky values for comparison
        ghi_clear_available = "ghi_clear" in fc_processed.columns
        clearsky_index_available = "clearsky_index" in fc_processed.columns
        
        forecast_data = []
        for i, time_str in enumerate(forecast_times):
            forecast_item = {
                "time": time_str,
                "timestamp": fc_processed["time"].iloc[i].isoformat(),
                "p10": float(predictions["p10"][i]),
                "p50": float(predictions["p50"][i]),
                "p90": float(predictions["p90"][i]),
                "mean": float(predictions["mean"][i]),
                "std": float(predictions["std"][i]),
                "ghi": float(predictions["mean"][i])  # Use mean as point estimate
            }
            
            # Add clear-sky comparison if available
            if ghi_clear_available:
                ghi_clear_val = float(fc_processed["ghi_clear"].iloc[i])
                forecast_item["ghi_clear_sky"] = ghi_clear_val
                
                # Calculate ratio only if clear-sky > 0 (avoid division by zero)
                if ghi_clear_val > 1.0:  # Only calculate if meaningful clear-sky value
                    forecast_item["clear_sky_ratio"] = float(predictions["mean"][i] / ghi_clear_val)
                else:
                    forecast_item["clear_sky_ratio"] = None  # Not meaningful at night
            
            if clearsky_index_available:
                csi_val = float(fc_processed["clearsky_index"].iloc[i])
                # Clip to reasonable range (0-1.5, where 1.0 = clear sky)
                forecast_item["clear_sky_index"] = float(np.clip(csi_val, 0.0, 1.5))
            
            # Add solar elevation for context
            if "solar_elevation" in fc_processed.columns:
                solar_elev = float(fc_processed["solar_elevation"].iloc[i])
                forecast_item["solar_elevation"] = solar_elev
                forecast_item["is_daytime"] = solar_elev > 5.0  # Daytime if elevation > 5 degrees
            
            forecast_data.append(forecast_item)
        
        # Calculate summary statistics
        mean_ghi = np.mean([f["ghi"] for f in forecast_data])
        max_ghi = np.max([f["ghi"] for f in forecast_data])
        min_ghi = np.min([f["ghi"] for f in forecast_data])
        
        # Calculate average uncertainty
        avg_uncertainty = np.mean([f["std"] for f in forecast_data])
        
        return {
            "status": "ok",
            "model": "ngboost",
            "location": {"lat": lat, "lon": lon},
            "horizon_hours": horizon_hours,
            "forecast": forecast_data,
            "summary": {
                "mean_ghi": float(mean_ghi),
                "max_ghi": float(max_ghi),
                "min_ghi": float(min_ghi),
                "avg_uncertainty": float(avg_uncertainty)
            },
            "metadata": {
                "data_source": "open-meteo",
                "retrained": retrain,
                "training_days": training_days,
                "n_samples": len(forecast_data),
                "features_used": len(model.feature_cols) if model.feature_cols else 0
            }
        }
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Missing required dependency. Install with: pip install ngboost pvlib"
        )
    except Exception as e:
        logger.error(f"Error generating NGBoost forecast: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate forecast: {str(e)}"
        )


@router.get("/hybrid")
async def get_hybrid_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    horizon_hours: int = Query(24, ge=1, le=48, description="Forecast horizon in hours"),
    use_satellite: bool = Query(True, description="Include satellite cloud data if available"),
    training_days: int = Query(180, ge=30, le=730, description="Days of historical data for training")
):
    """
    Hybrid forecast combining Open-Meteo weather data with satellite cloud imagery.
    Provides the best of both worlds: weather model data + real-time cloud observations.
    
    Features:
    - Open-Meteo weather data (temperature, humidity, pressure, etc.)
    - Satellite cloud imagery (if available)
    - Enhanced feature engineering
    - Probabilistic forecasts with uncertainty
    - Clear-sky comparison
    """
    try:
        from app.services.open_meteo_service import OpenMeteoService
        from app.services.satellite_ingest import SatelliteDataIngester
        from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data
        from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel
        from app.core.config import settings
        import numpy as np
        
        logger.info(f"Fetching hybrid forecast for ({lat}, {lon}), horizon={horizon_hours}h")
        
        # Initialize services
        meteo_service = OpenMeteoService()
        satellite_ingester = SatelliteDataIngester(use_mock=settings.USE_MOCK_DATA)
        
        # Fetch Open-Meteo data
        logger.info("Fetching Open-Meteo data...")
        hist_df, fc_df = meteo_service.fetch_combined(
            lat=lat,
            lon=lon,
            past_days=training_days,
            forecast_hours=horizon_hours
        )
        
        # Try to fetch satellite data if requested
        satellite_features = {}
        if use_satellite:
            try:
                logger.info("Fetching satellite cloud data...")
                current_image = await satellite_ingester.fetch_latest_image(lat, lon, radius_km=50)
                
                # Extract cloud features from satellite image
                if current_image is not None and current_image.size > 0:
                    # Simple cloud detection from satellite image
                    gray = np.mean(current_image[:, :, :3], axis=2) if len(current_image.shape) == 3 else current_image
                    cloud_coverage = np.mean(gray > 200) / 255.0  # Normalize
                    avg_brightness = np.mean(gray) / 255.0
                    
                    satellite_features = {
                        "satellite_cloud_coverage": float(cloud_coverage),
                        "satellite_brightness": float(avg_brightness),
                        "satellite_available": True
                    }
                    logger.info(f"Satellite features extracted: cloud_coverage={cloud_coverage:.2f}")
                else:
                    satellite_features = {"satellite_available": False}
            except Exception as e:
                logger.warning(f"Satellite data not available: {e}")
                satellite_features = {"satellite_available": False}
        
        # Preprocess Open-Meteo data
        logger.info("Preprocessing data...")
        df_processed = preprocess_open_meteo_data(
            hist_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=horizon_hours
        )
        
        # Add satellite features if available (for training)
        if satellite_features.get("satellite_available") and len(df_processed) > 0:
            # Add satellite features as additional columns
            for key, value in satellite_features.items():
                if key != "satellite_available":
                    df_processed[key] = value
        
        # Load or train model
        model_path = Path("data/models/ngboost_hybrid_24h.joblib")
        feature_path = Path("data/models/ngboost_hybrid_features.joblib")
        
        # Always retrain for hybrid to incorporate latest satellite data
        logger.info("Training hybrid NGBoost model...")
        model = NGBoostIrradianceModel(n_estimators=600, learning_rate=0.03)
        target_col = f"target_{horizon_hours}h"
        metrics = model.train(
            df_processed,
            target_col=target_col,
            save_path=str(model_path),
            feature_cols_path=str(feature_path)
        )
        
        # Preprocess forecast data
        fc_processed = preprocess_open_meteo_data(
            fc_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=0
        )
        
        # Add satellite features to forecast data if available
        if satellite_features.get("satellite_available"):
            for key, value in satellite_features.items():
                if key != "satellite_available":
                    fc_processed[key] = value
        
        # Make predictions
        logger.info("Generating hybrid predictions...")
        predictions = model.predict(fc_processed, return_uncertainty=True)
        
        # Format response
        forecast_times = fc_processed["time_local"].dt.strftime("%Y-%m-%d %H:%M").tolist()
        
        ghi_clear_available = "ghi_clear" in fc_processed.columns
        
        forecast_data = []
        for i, time_str in enumerate(forecast_times):
            forecast_item = {
                "time": time_str,
                "timestamp": fc_processed["time"].iloc[i].isoformat(),
                "p10": float(predictions["p10"][i]),
                "p50": float(predictions["p50"][i]),
                "p90": float(predictions["p90"][i]),
                "mean": float(predictions["mean"][i]),
                "std": float(predictions["std"][i]),
                "ghi": float(predictions["mean"][i])
            }
            
            if ghi_clear_available:
                forecast_item["ghi_clear_sky"] = float(fc_processed["ghi_clear"].iloc[i])
                forecast_item["clear_sky_ratio"] = float(predictions["mean"][i] / (fc_processed["ghi_clear"].iloc[i] + 1e-9))
            
            if "solar_elevation" in fc_processed.columns:
                forecast_item["solar_elevation"] = float(fc_processed["solar_elevation"].iloc[i])
            
            forecast_data.append(forecast_item)
        
        # Summary statistics
        mean_ghi = np.mean([f["ghi"] for f in forecast_data])
        max_ghi = np.max([f["ghi"] for f in forecast_data])
        min_ghi = np.min([f["ghi"] for f in forecast_data])
        avg_uncertainty = np.mean([f["std"] for f in forecast_data])
        
        return {
            "status": "ok",
            "model": "hybrid_ngboost",
            "location": {"lat": lat, "lon": lon},
            "horizon_hours": horizon_hours,
            "forecast": forecast_data,
            "summary": {
                "mean_ghi": float(mean_ghi),
                "max_ghi": float(max_ghi),
                "min_ghi": float(min_ghi),
                "avg_uncertainty": float(avg_uncertainty)
            },
            "satellite": satellite_features,
            "model_metrics": metrics,
            "metadata": {
                "data_sources": ["open-meteo"] + (["satellite"] if satellite_features.get("satellite_available") else []),
                "training_days": training_days,
                "n_samples": len(forecast_data),
                "features_used": len(model.feature_cols) if model.feature_cols else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating hybrid forecast: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate hybrid forecast: {str(e)}"
        )
