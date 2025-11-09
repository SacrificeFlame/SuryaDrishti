"""
Microgrid-specific forecast endpoints.
Converts GHI forecasts to power output and provides microgrid-optimized forecasts.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import Microgrid
from app.services.open_meteo_service import OpenMeteoService
from app.ml.preprocessing.open_meteo_preprocess import preprocess_open_meteo_data
from app.ml.models.irradiance_forecast.ngboost_model import NGBoostIrradianceModel
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import asyncio
from typing import Optional, Dict, List
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)

# Timeout configuration
FORECAST_TIMEOUT_SECONDS = 45  # Total timeout for forecast generation
METEO_FETCH_TIMEOUT_SECONDS = 20  # Timeout for Open-Meteo API calls


def ghi_to_power(
    ghi_w_m2: float, 
    capacity_kw: float, 
    system_losses: float = 0.15,
    temperature_derating: float = 0.05,
    pollution_factor: float = 0.95,
    soiling_factor: float = 0.97
) -> float:
    """
    Convert Global Horizontal Irradiance (GHI) to power output with realistic losses.
    
    Standard conversion: At 1000 W/m² (STC), panels produce rated capacity.
    Accounts for multiple loss factors:
    - System losses (inverter, wiring): 15%
    - Temperature derating (Delhi avg ~45°C): 5%
    - Pollution/haze (Delhi AQI): 5% reduction
    - Soiling (dust accumulation): 3% reduction
    
    Total realistic efficiency: ~77% (0.85 * 0.95 * 0.95 * 0.97)
    
    Args:
        ghi_w_m2: Global Horizontal Irradiance in W/m²
        capacity_kw: Installed solar panel capacity in kW (rated at STC)
        system_losses: System losses including inverter, wiring, etc. (default 15%)
        temperature_derating: Temperature-related efficiency loss (default 5% for Delhi)
        pollution_factor: Air quality impact (default 0.95 = 5% loss for Delhi)
        soiling_factor: Dust/soiling impact (default 0.97 = 3% loss)
    
    Returns:
        Power output in kW
    """
    # Power = (GHI / 1000) * Capacity * (1 - system_losses) * temp_factor * pollution * soiling
    # At 1000 W/m², panels produce rated capacity (accounting for all losses)
    power_kw = (
        (ghi_w_m2 / 1000.0) * 
        capacity_kw * 
        (1 - system_losses) * 
        (1 - temperature_derating) * 
        pollution_factor * 
        soiling_factor
    )
    
    # Cap at rated capacity (can't exceed nameplate)
    return max(0.0, min(power_kw, capacity_kw))


def apply_realistic_ghi_bounds(
    ghi_w_m2: float,
    solar_elevation: float,
    ghi_clear_sky: Optional[float] = None,
    max_ghi_w_m2: float = 1000.0
) -> float:
    """
    Apply realistic bounds to GHI predictions based on physics and Delhi conditions.
    
    Realistic bounds:
    - Maximum GHI: ~800-1000 W/m² at peak (clear sky, high sun)
    - Should not exceed clear-sky GHI by more than 10% (accounting for model uncertainty)
    - Should scale with solar elevation (lower elevation = lower max possible GHI)
    
    Args:
        ghi_w_m2: Raw GHI prediction from model
        solar_elevation: Solar elevation angle in degrees
        ghi_clear_sky: Clear-sky GHI (if available)
        max_ghi_w_m2: Absolute maximum GHI (default 1000 W/m² for Delhi)
    
    Returns:
        Bounded GHI value
    """
    # If solar elevation is very low (< 5°), GHI should be very low
    if solar_elevation < 5.0:
        # At low elevation, max GHI is limited by atmospheric path length
        max_at_elevation = max_ghi_w_m2 * np.sin(np.radians(solar_elevation)) if solar_elevation > 0 else 0
        return min(ghi_w_m2, max_at_elevation)
    
    # If clear-sky is available, don't exceed it by more than 10%
    # (allows for slight model overestimation, but prevents unrealistic values)
    if ghi_clear_sky is not None and ghi_clear_sky > 10.0:
        max_allowed = ghi_clear_sky * 1.10  # Allow 10% over clear-sky
        ghi_w_m2 = min(ghi_w_m2, max_allowed)
    
    # Absolute maximum cap (Delhi peak is ~800-1000 W/m² under perfect conditions)
    ghi_w_m2 = min(ghi_w_m2, max_ghi_w_m2)
    
    # Scale with solar elevation for more realistic values
    # At 90° elevation (overhead), full value; at 30°, ~50% of peak
    if solar_elevation > 0:
        elevation_factor = np.sin(np.radians(solar_elevation))
        # Don't reduce too much if elevation is reasonable (> 20°)
        if solar_elevation > 20.0:
            elevation_factor = min(elevation_factor, 1.0)
        # Apply gentle scaling for very high values
        if ghi_w_m2 > 700.0:
            ghi_w_m2 = 700.0 + (ghi_w_m2 - 700.0) * elevation_factor
    
    return max(0.0, ghi_w_m2)


@router.get("/microgrid/{microgrid_id}")
async def get_microgrid_forecast(
    microgrid_id: str,
    horizon_hours: int = Query(24, ge=1, le=48, description="Forecast horizon in hours"),
    training_days: int = Query(180, ge=30, le=730, description="Days of historical data for training (not used with external API)"),
    retrain: bool = Query(False, description="Retrain model (not used with external API)"),
    db: Session = Depends(get_db)
):
    """
    Get solar irradiance and power output forecast for a specific microgrid.
    
    This endpoint uses the external forecast API at /api/run with source="hybrid".
    
    Returns:
    - GHI forecasts (W/m²) with uncertainty
    - Power output forecasts (kW) with uncertainty
    - Energy production estimates (kWh)
    """
    try:
        logger.info(f"Fetching forecast for microgrid {microgrid_id} (horizon={horizon_hours}h) from external API")
        
        # Get microgrid details
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        lat, lon = microgrid.latitude, microgrid.longitude
        capacity_kw = microgrid.capacity_kw
        
        logger.info(f"Microgrid {microgrid_id}: location=({lat}, {lon}), capacity={capacity_kw}kW")
        
        # Fetch from external API
        try:
            from app.services.external_forecast_service import (
                fetch_forecast_from_external_api,
                parse_external_api_response,
                convert_to_microgrid_forecast_format
            )
            
            external_data = await fetch_forecast_from_external_api(source="hybrid")
            logger.info("Successfully fetched data from external API")
            
            # Parse the response
            parsed_forecast = parse_external_api_response(external_data)
            logger.info(f"Parsed forecast contains {len(parsed_forecast.get('forecast', []))} points")
            
            # Convert to microgrid forecast format
            result = convert_to_microgrid_forecast_format(
                parsed_forecast,
                microgrid_id,
                lat,
                lon,
                capacity_kw
            )
            
            # Limit to requested horizon_hours
            if len(result['forecast']) > horizon_hours:
                result['forecast'] = result['forecast'][:horizon_hours]
                result['horizon_hours'] = horizon_hours
                # Recalculate summary with limited data
                ghi_values = [p["ghi"]["mean"] for p in result['forecast']]
                power_values = [p["power_kw"]["mean"] for p in result['forecast']]
                import numpy as np
                result['summary'] = {
                    "ghi": {
                        "mean": float(np.mean(ghi_values)) if ghi_values else 0.0,
                        "max": float(np.max(ghi_values)) if ghi_values else 0.0,
                        "min": float(np.min(ghi_values)) if ghi_values else 0.0
                    },
                    "power_kw": {
                        "mean": float(np.mean(power_values)) if power_values else 0.0,
                        "max": float(np.max(power_values)) if power_values else 0.0,
                        "min": float(np.min(power_values)) if power_values else 0.0
                    },
                    "total_energy_kwh": float(sum([p["energy_kwh"] for p in result['forecast']])),
                    "avg_uncertainty": float(np.mean([p["ghi"]["std"] for p in result['forecast']])) if result['forecast'] else 0.0
                }
            
            logger.info(f"Successfully generated forecast: {len(result['forecast'])} points")
            return result
            
        except Exception as e:
            logger.error(f"External API call failed: {e}", exc_info=True)
            logger.warning("External API unavailable. Using internal NGBoost forecast with Open-Meteo data.")
            
            # Use internal forecast generation (REAL DATA from Open-Meteo + NGBoost)
            try:
                result = await asyncio.wait_for(
                    _generate_forecast_internal(
                        microgrid_id,
                        horizon_hours,
                        training_days,
                        retrain,
                        db
                    ),
                    timeout=FORECAST_TIMEOUT_SECONDS
                )
                logger.info(f"Successfully generated internal forecast: {len(result['forecast'])} points")
                # Add metadata note
                if 'metadata' in result:
                    result['metadata']['data_source'] = 'internal_ngboost_openmeteo'
                    result['metadata']['external_api_error'] = str(e)[:100]
                return result
            except asyncio.TimeoutError:
                logger.error(f"Internal forecast generation timed out after {FORECAST_TIMEOUT_SECONDS}s")
                raise HTTPException(
                    status_code=500,
                    detail=f"Forecast generation timed out after {FORECAST_TIMEOUT_SECONDS} seconds"
                )
            except Exception as internal_error:
                logger.error(f"Internal forecast generation failed: {internal_error}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"All forecast methods failed. External API: {str(e)[:100]}, Internal: {str(internal_error)[:100]}"
                )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast for microgrid {microgrid_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate forecast: {str(e)[:200]}"
        )


async def _generate_forecast_internal(
    microgrid_id: str,
    horizon_hours: int,
    training_days: int,
    retrain: bool,
    db: Session
) -> Dict:
    """Internal forecast generation function (called with timeout wrapper)."""
    try:
        # Get microgrid details
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        lat, lon = microgrid.latitude, microgrid.longitude
        capacity_kw = microgrid.capacity_kw
        
        logger.info(f"Generating forecast for microgrid {microgrid_id} at ({lat}, {lon}), capacity={capacity_kw}kW")
        
        # Initialize services
        meteo_service = OpenMeteoService()
        
        # Fetch data using microgrid coordinates with timeout
        logger.info("Fetching Open-Meteo data for microgrid location...")
        try:
            # Wrap the synchronous fetch in a thread executor with timeout
            loop = asyncio.get_event_loop()
            hist_df, fc_df = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: meteo_service.fetch_combined(
                        lat=lat,
                        lon=lon,
                        past_days=training_days,
                        forecast_hours=horizon_hours
                    )
                ),
                timeout=METEO_FETCH_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            logger.warning(f"Open-Meteo API call timed out after {METEO_FETCH_TIMEOUT_SECONDS}s")
            raise Exception("Open-Meteo API timeout")
        
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
        
        # Preprocess forecast data
        fc_processed = preprocess_open_meteo_data(
            fc_df,
            lat=lat,
            lon=lon,
            target_horizon_hours=0
        )
        
        # Make predictions
        logger.info("Generating predictions...")
        predictions = model.predict(fc_processed, return_uncertainty=True)
        
        # Debug: Log first few predictions to verify model is working
        if len(predictions.get("mean", [])) > 0:
            logger.info(f"Sample RAW predictions (first 10): {predictions['mean'][:10]}")
            if "solar_elevation" in fc_processed.columns:
                logger.info(f"Sample solar elevations (first 10): {fc_processed['solar_elevation'].head(10).tolist()}")
            if "time_local" in fc_processed.columns:
                logger.info(f"Sample local times (first 10): {fc_processed['time_local'].head(10).dt.strftime('%Y-%m-%d %H:%M').tolist()}")
                # Also log the hours for daytime check
                hours = fc_processed['time_local'].head(10).dt.hour.tolist()
                logger.info(f"Sample local hours (first 10): {hours}")
        
        # Format response with power conversion
        # Create forecast_times first before logging
        if "time_local" in fc_processed.columns:
            forecast_times = fc_processed["time_local"].dt.strftime("%Y-%m-%d %H:%M").tolist()
        else:
            forecast_times = fc_processed["time"].dt.strftime("%Y-%m-%d %H:%M").tolist()
        
        # Log all forecast times and their daytime status for debugging
        logger.info(f"Total forecast points: {len(forecast_times)}")
        if len(forecast_times) > 0:
            logger.info(f"First forecast time: {forecast_times[0]}")
            logger.info(f"Last forecast time: {forecast_times[-1]}")
        
        ghi_clear_available = "ghi_clear" in fc_processed.columns
        
        forecast_data = []
        total_energy_kwh = 0.0
        
        for i, time_str in enumerate(forecast_times):
            # Get raw predictions from model FIRST (before any daytime checks)
            ghi_mean_raw = float(predictions["mean"][i])
            ghi_p10_raw = float(predictions["p10"][i])
            ghi_p50_raw = float(predictions["p50"][i])
            ghi_p90_raw = float(predictions["p90"][i])
            ghi_std_raw = float(predictions["std"][i])
            
            # Check if it's nighttime using solar elevation (most accurate) or timestamp
            is_daytime = False  # Default to nighttime for safety
            solar_elev = None
            
            # First, try to use solar elevation (most accurate - accounts for actual sunrise/sunset)
            if "solar_elevation" in fc_processed.columns:
                solar_elev = float(fc_processed["solar_elevation"].iloc[i])
                # Sun is above horizon if elevation > 0 degrees
                # Use a small threshold (-0.5°) to account for atmospheric refraction
                # (sun can be slightly below horizon but still provide twilight)
                if solar_elev > -0.5:
                    is_daytime = True
                # If solar elevation is very low (< -0.5°), fall through to time-based check
                # (solar elevation might be incorrectly calculated or deep twilight)
            
            # Fallback: check hour from LOCAL time (IST) if solar elevation unavailable or very low
            # But prioritize solar elevation - if it's negative, it's definitely nighttime
            if not is_daytime and solar_elev is not None:
                # If solar elevation is negative, it's definitely nighttime (don't override)
                if solar_elev < -0.5:
                    is_daytime = False
                elif solar_elev > 0:
                    # Solar elevation is positive, so it's daytime
                    is_daytime = True
            elif not is_daytime:
                # Solar elevation not available, use time-based check as last resort
                if "time_local" in fc_processed.columns:
                    local_time = fc_processed["time_local"].iloc[i]
                    if isinstance(local_time, pd.Timestamp):
                        hour = local_time.hour
                        minute = local_time.minute
                        # Use conservative daytime window: 6:30 AM to 6:30 PM IST
                        # This accounts for actual sunrise times (typically 6:30-6:40 AM in November)
                        total_minutes = hour * 60 + minute
                        # Daytime: 6:30 AM (390 min) to 6:30 PM (1110 min) - more conservative
                        is_daytime = total_minutes >= 390 and total_minutes < 1110
                else:
                    # Last resort: use UTC time and convert to IST
                    timestamp = fc_processed["time"].iloc[i]
                    if isinstance(timestamp, pd.Timestamp):
                        # Convert UTC to IST (UTC+5:30)
                        ist_hour = timestamp.hour + 5
                        ist_minute = timestamp.minute + 30
                        if ist_minute >= 60:
                            ist_minute -= 60
                            ist_hour += 1
                        ist_hour = ist_hour % 24
                        total_minutes = ist_hour * 60 + ist_minute
                        # Daytime: 6:00 AM (360 min) to 7:00 PM (1140 min) IST
                        is_daytime = total_minutes >= 360 and total_minutes < 1140
            
            # Debug logging for first few points
            if i < 5:
                logger.info(f"Point {i}: time={time_str}, solar_elev={solar_elev}, is_daytime={is_daytime}, raw_ghi={ghi_mean_raw:.1f}")
            
            # Get clear-sky GHI for realistic bounds checking
            ghi_clear_val = None
            if ghi_clear_available:
                ghi_clear_val = float(fc_processed["ghi_clear"].iloc[i]) if fc_processed["ghi_clear"].iloc[i] > 1.0 else None
            
            # At night, set GHI and power to zero (physics: no sun = no power)
            # Use solar elevation as definitive check - if sun is below horizon, no power
            if not is_daytime or (solar_elev is not None and solar_elev < -0.5):
                # It's clearly nighttime - zero out all values
                # Don't trust model predictions if solar elevation is negative (sun is below horizon)
                ghi_mean = 0.0
                ghi_p10 = 0.0
                ghi_p50 = 0.0
                ghi_p90 = 0.0
                ghi_std = 0.0
                is_daytime = False  # Ensure it's marked as nighttime
            else:
                # Daytime: apply realistic bounds to model predictions
                # This prevents overly optimistic forecasts (e.g., 850 W/m² staying high for hours)
                ghi_mean = apply_realistic_ghi_bounds(
                    ghi_mean_raw, 
                    solar_elev if solar_elev is not None else 0.0,
                    ghi_clear_val,
                    max_ghi_w_m2=1000.0  # Delhi peak ~800-1000 W/m²
                )
                ghi_p10 = apply_realistic_ghi_bounds(
                    ghi_p10_raw,
                    solar_elev if solar_elev is not None else 0.0,
                    ghi_clear_val,
                    max_ghi_w_m2=1000.0
                )
                ghi_p50 = apply_realistic_ghi_bounds(
                    ghi_p50_raw,
                    solar_elev if solar_elev is not None else 0.0,
                    ghi_clear_val,
                    max_ghi_w_m2=1000.0
                )
                ghi_p90 = apply_realistic_ghi_bounds(
                    ghi_p90_raw,
                    solar_elev if solar_elev is not None else 0.0,
                    ghi_clear_val,
                    max_ghi_w_m2=1000.0
                )
                ghi_std = ghi_std_raw
            
            # Convert GHI to power output with realistic losses
            # For Delhi: pollution factor 0.95, soiling 0.97, temp derating 0.05
            # Total efficiency: ~77% (more realistic than 85%)
            power_mean = ghi_to_power(
                ghi_mean, 
                capacity_kw,
                system_losses=0.15,
                temperature_derating=0.05,  # Delhi avg temp ~45°C
                pollution_factor=0.95,  # Delhi AQI impact
                soiling_factor=0.97  # Dust accumulation
            )
            power_p10 = ghi_to_power(ghi_p10, capacity_kw, 0.15, 0.05, 0.95, 0.97)
            power_p50 = ghi_to_power(ghi_p50, capacity_kw, 0.15, 0.05, 0.95, 0.97)
            power_p90 = ghi_to_power(ghi_p90, capacity_kw, 0.15, 0.05, 0.95, 0.97)
            
            # Energy production (kWh) for this hour
            energy_kwh = power_mean * 1.0  # 1 hour interval
            
            forecast_item = {
                "time": time_str,
                "timestamp": fc_processed["time"].iloc[i].isoformat(),
                # Irradiance data
                "ghi": {
                    "p10": ghi_p10,
                    "p50": ghi_p50,
                    "p90": ghi_p90,
                    "mean": ghi_mean,
                    "std": ghi_std
                },
                # Power output data
                "power_kw": {
                    "p10": power_p10,
                    "p50": power_p50,
                    "p90": power_p90,
                    "mean": power_mean
                },
                # Energy production
                "energy_kwh": energy_kwh
            }
            
            # Add clear-sky comparison if available
            if ghi_clear_available and ghi_clear_val is not None:
                forecast_item["ghi"]["clear_sky"] = ghi_clear_val
                if ghi_clear_val > 1.0:
                    forecast_item["ghi"]["clear_sky_ratio"] = float(ghi_mean / ghi_clear_val)
                    # Clear-sky power with same realistic losses
                    forecast_item["power_kw"]["clear_sky"] = ghi_to_power(
                        ghi_clear_val, capacity_kw, 0.15, 0.05, 0.95, 0.97
                    )
            
            # Add solar elevation for context
            if "solar_elevation" in fc_processed.columns:
                forecast_item["solar_elevation"] = float(fc_processed["solar_elevation"].iloc[i])
                forecast_item["is_daytime"] = is_daytime  # Use the calculated is_daytime value
            else:
                forecast_item["is_daytime"] = is_daytime  # Set from hour check
            
            forecast_data.append(forecast_item)
            total_energy_kwh += energy_kwh
        
        # Calculate summary statistics
        ghi_values = [f["ghi"]["mean"] for f in forecast_data]
        power_values = [f["power_kw"]["mean"] for f in forecast_data]
        
        # Calculate realistic capacity factor (power / capacity)
        max_power = max(power_values) if power_values else 0.0
        avg_power = np.mean(power_values) if power_values else 0.0
        capacity_factor_max = (max_power / capacity_kw * 100) if capacity_kw > 0 else 0.0
        capacity_factor_avg = (avg_power / capacity_kw * 100) if capacity_kw > 0 else 0.0
        
        # Generate warnings if values seem unrealistic
        warnings: List[str] = []
        if max_power > capacity_kw * 0.85:
            warnings.append(f"Peak power ({max_power:.1f} kW) exceeds 85% of capacity - may be optimistic for Delhi conditions")
        if capacity_factor_max > 85.0:
            warnings.append(f"Peak capacity factor ({capacity_factor_max:.1f}%) is very high - verify site conditions")
        if max(ghi_values) > 900.0:
            warnings.append(f"Peak GHI ({max(ghi_values):.1f} W/m²) is very high - verify clear-sky conditions")
        
        return {
            "status": "ok",
            "model": "ngboost_microgrid",
            "microgrid": {
                "id": microgrid_id,
                "name": microgrid.name,
                "location": {"lat": lat, "lon": lon},
                "capacity_kw": capacity_kw
            },
            "horizon_hours": horizon_hours,
            "forecast": forecast_data,
            "summary": {
                "ghi": {
                    "mean": float(np.mean(ghi_values)),
                    "max": float(np.max(ghi_values)),
                    "min": float(np.min(ghi_values))
                },
                "power_kw": {
                    "mean": float(np.mean(power_values)),
                    "max": float(np.max(power_values)),
                    "min": float(np.min(power_values))
                },
                "total_energy_kwh": float(total_energy_kwh),
                "avg_uncertainty": float(np.mean([f["ghi"]["std"] for f in forecast_data])),
                "capacity_factor": {
                    "peak_percent": float(capacity_factor_max),
                    "average_percent": float(capacity_factor_avg)
                },
                "warnings": warnings if warnings else None
            },
            "metadata": {
                "data_source": "open-meteo",
                "retrained": retrain,
                "training_days": training_days,
                "n_samples": len(forecast_data),
                "features_used": len(model.feature_cols) if model.feature_cols else 0
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in internal forecast generation: {e}", exc_info=True)
        raise  # Re-raise to be caught by outer handler

