"""
External Forecast API Service
Handles communication with the external forecast API at /api/run
"""
import httpx
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pytz
import pvlib
import pandas as pd

logger = logging.getLogger(__name__)

EXTERNAL_API_URL = "http://127.0.0.1:8000/api/run"
EXTERNAL_API_KEY = "aryan1234%^&*()"
REQUEST_TIMEOUT = 60.0  # 60 seconds timeout (increased for model training/loading)

def get_external_api_url_with_bypass():
    """Get external API URL with ngrok bypass parameter if needed"""
    base_url = EXTERNAL_API_URL
    if "ngrok-free.dev" in base_url or "ngrok.io" in base_url:
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}ngrok-skip-browser-warning=true"
    return base_url


async def fetch_forecast_from_external_api(source: str = "hybrid") -> Dict:
    """
    Fetch forecast data from external API.
    
    Args:
        source: Forecast source type (default: "hybrid")
    
    Returns:
        Dictionary with forecast data from external API
    
    Raises:
        Exception: If API call fails or times out
    """
    try:
        # Get URL with ngrok bypass if needed
        api_url = get_external_api_url_with_bypass()
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": EXTERNAL_API_KEY,
                "ngrok-skip-browser-warning": "true",  # Bypass ngrok browser warning
            }
            
            payload = {"source": source}
            
            logger.info(f"Calling external forecast API: {api_url} with source={source}")
            
            response = await client.post(
                api_url,
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"External API returned status {response.status_code}")
            logger.debug(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
            return data
            
    except httpx.TimeoutException:
        logger.error(f"External forecast API timeout after {REQUEST_TIMEOUT}s")
        raise Exception(f"External API timeout after {REQUEST_TIMEOUT} seconds")
    except httpx.HTTPStatusError as e:
        logger.error(f"External forecast API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        raise Exception(f"External API returned status {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        logger.error(f"Error calling external forecast API: {e}")
        raise


def parse_external_api_response(external_data: Dict) -> Dict:
    """
    Parse external API response and extract forecast data.
    Handles various possible response structures.
    
    Args:
        external_data: Raw response from external API
    
    Returns:
        Dictionary with 'forecast' key containing forecast points
    
    Raises:
        ValueError: If response format is not recognized
    """
    if not isinstance(external_data, dict):
        raise ValueError(f"External API response is not a dictionary: {type(external_data)}")
    
    logger.info(f"Parsing external API response. Top-level keys: {list(external_data.keys())}")
    
    # Try different possible response structures
    forecast_data = None
    
    # Structure 1: Direct forecast key
    if 'forecast' in external_data:
        forecast_data = external_data
        logger.info("Found 'forecast' key at top level")
    
    # Structure 2: Nested in 'data'
    elif 'data' in external_data:
        data = external_data['data']
        if isinstance(data, dict):
            if 'forecast' in data:
                forecast_data = data
                logger.info("Found 'forecast' key in 'data'")
            else:
                # Check if data itself is a list (could be forecast points directly)
                if isinstance(data, list) and len(data) > 0:
                    # Assume data is the forecast array
                    forecast_data = {'forecast': data}
                    logger.info("Found forecast array in 'data' key")
                else:
                    forecast_data = external_data
        else:
            forecast_data = external_data
    
    # Structure 3: Nested in 'output'
    elif 'output' in external_data:
        output = external_data.get('output', {})
        if isinstance(output, dict):
            if 'forecast' in output:
                forecast_data = output
                logger.info("Found 'forecast' key in 'output'")
            elif 'data' in output and isinstance(output['data'], dict):
                if 'forecast' in output['data']:
                    forecast_data = output['data']
                    logger.info("Found 'forecast' key in 'output.data'")
                else:
                    forecast_data = output
            else:
                forecast_data = output
        elif isinstance(output, list):
            # Output is directly a list of forecast points
            forecast_data = {'forecast': output}
            logger.info("Found forecast array in 'output' key")
        else:
            forecast_data = external_data
    
    # Structure 4: Check if response is a list directly (unlikely but possible)
    elif isinstance(external_data, list):
        forecast_data = {'forecast': external_data}
        logger.info("Response is a list, treating as forecast array")
    
    # Structure 5: Check for other common keys
    else:
        # Look for any key that might contain forecast data
        for key in ['result', 'response', 'forecasts', 'predictions']:
            if key in external_data:
                value = external_data[key]
                if isinstance(value, list):
                    forecast_data = {'forecast': value}
                    logger.info(f"Found forecast array in '{key}' key")
                    break
                elif isinstance(value, dict) and 'forecast' in value:
                    forecast_data = value
                    logger.info(f"Found 'forecast' key in '{key}'")
                    break
        
        if not forecast_data:
            forecast_data = external_data
    
    # Final validation
    if not forecast_data:
        available_keys = list(external_data.keys()) if isinstance(external_data, dict) else []
        raise ValueError(
            f"Could not parse external API response. "
            f"Available keys: {available_keys}"
        )
    
    # Ensure forecast key exists
    if 'forecast' not in forecast_data:
        # Check if any value is a list (might be forecast points)
        for key, value in forecast_data.items():
            if isinstance(value, list) and len(value) > 0:
                # Check if first item looks like a forecast point
                first_item = value[0]
                if isinstance(first_item, dict) and any(k in first_item for k in ['timestamp', 'time', 'ghi', 'power']):
                    forecast_data = {'forecast': value}
                    logger.info(f"Found forecast array in '{key}' key (detected by structure)")
                    break
        
        if 'forecast' not in forecast_data:
            available_keys = list(forecast_data.keys()) if isinstance(forecast_data, dict) else []
            raise ValueError(
                f"External API response doesn't contain 'forecast' key. "
                f"Available keys: {available_keys}. "
                f"Please check the API response format."
            )
    
    forecast_points = forecast_data.get('forecast', [])
    if not isinstance(forecast_points, list):
        raise ValueError(f"Forecast data is not a list: {type(forecast_points)}")
    
    if len(forecast_points) == 0:
        raise ValueError("External API forecast is empty")
    
    logger.info(f"Successfully parsed {len(forecast_points)} forecast points")
    return forecast_data


def convert_to_microgrid_forecast_format(
    external_forecast: Dict,
    microgrid_id: str,
    lat: float,
    lon: float,
    capacity_kw: float
) -> Dict:
    """
    Convert external API forecast format to MicrogridForecastResponse format.
    
    Args:
        external_forecast: Parsed forecast data from external API
        microgrid_id: Microgrid identifier
        lat: Latitude
        lon: Longitude
        capacity_kw: Solar capacity in kW
    
    Returns:
        Dictionary in MicrogridForecastResponse format
    """
    # Import ghi_to_power function (defined in forecast_microgrid module)
    from app.api.v1.forecast_microgrid import ghi_to_power
    
    forecast_points = external_forecast.get('forecast', [])
    
    if not forecast_points:
        raise ValueError("External API forecast is empty")
    
    # Convert each forecast point
    converted_points = []
    total_energy_kwh = 0.0
    
    for point in forecast_points:
        # Extract timestamp
        timestamp = point.get('timestamp') or point.get('time')
        if isinstance(timestamp, str):
            try:
                point_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                point_time = datetime.utcnow()
        else:
            point_time = datetime.utcnow()
        
        # Extract GHI data - handle multiple formats
        ghi_data = point.get('ghi', {})
        if isinstance(ghi_data, dict):
            # Try different possible keys for mean GHI
            ghi_mean = ghi_data.get('mean', ghi_data.get('ghi', ghi_data.get('value', 0)))
            ghi_p10 = ghi_data.get('p10', ghi_data.get('p10_value', ghi_mean * 0.8))
            ghi_p50 = ghi_data.get('p50', ghi_data.get('p50_value', ghi_mean))
            ghi_p90 = ghi_data.get('p90', ghi_data.get('p90_value', ghi_mean * 1.2))
            ghi_std = ghi_data.get('std', ghi_data.get('std_value', ghi_mean * 0.1))
        elif isinstance(ghi_data, (int, float)):
            # GHI is a direct number
            ghi_mean = float(ghi_data)
            ghi_p10 = ghi_mean * 0.8
            ghi_p50 = ghi_mean
            ghi_p90 = ghi_mean * 1.2
            ghi_std = ghi_mean * 0.1
        else:
            # Try to get GHI from other possible keys
            ghi_mean = float(point.get('ghi', point.get('irradiance', point.get('solar_irradiance', 0))))
            ghi_p10 = ghi_mean * 0.8
            ghi_p50 = ghi_mean
            ghi_p90 = ghi_mean * 1.2
            ghi_std = ghi_mean * 0.1
        
        # Extract power data (if available) - handle multiple formats
        power_data = point.get('power_kw', point.get('power', point.get('solar_power', {})))
        if isinstance(power_data, dict):
            power_mean = power_data.get('mean', power_data.get('value', power_data.get('power', 0)))
            power_p10 = power_data.get('p10', power_data.get('p10_value', power_mean * 0.8))
            power_p50 = power_data.get('p50', power_data.get('p50_value', power_mean))
            power_p90 = power_data.get('p90', power_data.get('p90_value', power_mean * 1.2))
        elif isinstance(power_data, (int, float)):
            # Power is a direct number
            power_mean = float(power_data)
            power_p10 = power_mean * 0.8
            power_p50 = power_mean
            power_p90 = power_mean * 1.2
        else:
            # Calculate from GHI if not provided
            power_mean = ghi_to_power(ghi_mean, capacity_kw)
            power_p10 = ghi_to_power(ghi_p10, capacity_kw)
            power_p50 = ghi_to_power(ghi_p50, capacity_kw)
            power_p90 = ghi_to_power(ghi_p90, capacity_kw)
        
        # Calculate IST time for daytime check
        ist_tz = pytz.timezone('Asia/Kolkata')
        if point_time.tzinfo is None:
            point_time_utc = pytz.utc.localize(point_time)
        else:
            point_time_utc = point_time
        point_time_ist = point_time_utc.astimezone(ist_tz)
        hour_ist = point_time_ist.hour
        minute_ist = point_time_ist.minute
        total_minutes_ist = hour_ist * 60 + minute_ist
        
        # Get solar elevation and daytime status from point (if available)
        solar_elevation = point.get('solar_elevation', None)
        is_daytime_from_point = point.get('is_daytime', None)
        
        # Calculate actual solar elevation if not provided (most accurate method)
        if solar_elevation is None or solar_elevation == 0:
            try:
                # Use pvlib to calculate actual solar elevation for this timestamp
                site = pvlib.location.Location(lat, lon, tz=ist_tz)
                # Create a pandas DatetimeIndex for this single timestamp
                time_index = pd.DatetimeIndex([point_time_ist])
                solpos = site.get_solarposition(time_index)
                solar_elevation = float(solpos['elevation'].iloc[0])
            except Exception as e:
                logger.debug(f"Could not calculate solar elevation: {e}, using time-based estimate")
                # Fallback: estimate based on time (conservative - only mark as daytime if clearly in daylight hours)
                # Use actual sunrise/sunset calculation if possible
                try:
                    site = pvlib.location.Location(lat, lon, tz=ist_tz)
                    # Get sunrise/sunset for this date
                    date_only = point_time_ist.date()
                    times = pd.date_range(start=f"{date_only} 00:00", end=f"{date_only} 23:59", freq='1H', tz=ist_tz)
                    solpos = site.get_solarposition(times)
                    # Find when sun is above horizon
                    sun_up = solpos['elevation'] > 0
                    if sun_up.any():
                        # Get first and last time sun is up
                        sun_up_times = times[sun_up]
                        if len(sun_up_times) > 0:
                            sunrise_time = sun_up_times[0]
                            sunset_time = sun_up_times[-1]
                            # Check if current time is between sunrise and sunset
                            is_daytime_by_sun = sunrise_time.time() <= point_time_ist.time() <= sunset_time.time()
                        else:
                            is_daytime_by_sun = False
                    else:
                        is_daytime_by_sun = False
                    
                    # Use actual solar elevation from pvlib for this specific time
                    if is_daytime_by_sun:
                        # Get actual solar elevation for this specific timestamp
                        time_index_single = pd.DatetimeIndex([point_time_ist])
                        solpos_single = site.get_solarposition(time_index_single)
                        solar_elevation = float(solpos_single['elevation'].iloc[0])
                    else:
                        solar_elevation = -10.0
                except Exception as e2:
                    logger.warning(f"Could not calculate sunrise/sunset: {e2}, using conservative time check")
                    # Last resort: use conservative time-based check (6:30 AM to 6:30 PM)
                    is_daytime_by_time = total_minutes_ist >= 390 and total_minutes_ist < 1110  # 6:30 AM to 6:30 PM
                    solar_elevation = max(0, 90 - abs(hour_ist - 12) * 15) if is_daytime_by_time else -10.0
        
        # Determine final daytime status using solar elevation (most accurate)
        # Sun is above horizon if elevation > 0 degrees (accounting for atmospheric refraction)
        # Use -0.5° threshold to account for twilight
        if solar_elevation is not None:
            is_daytime = solar_elevation > -0.5
        elif is_daytime_from_point is not None:
            is_daytime = bool(is_daytime_from_point)
        else:
            # Last resort: conservative time-based check
            is_daytime = total_minutes_ist >= 390 and total_minutes_ist < 1110  # 6:30 AM to 6:30 PM
        
        # CRITICAL: Ensure nighttime values are zero (physics: no sun = no power)
        # Use solar elevation as the definitive check (most accurate)
        if not is_daytime or (solar_elevation is not None and solar_elevation < -0.5):
            # It's clearly nighttime - zero out all values
            ghi_mean = 0.0
            ghi_p10 = 0.0
            ghi_p50 = 0.0
            ghi_p90 = 0.0
            ghi_std = 0.0
            power_mean = 0.0
            power_p10 = 0.0
            power_p50 = 0.0
            power_p90 = 0.0
            is_daytime = False
            solar_elevation = -10.0 if solar_elevation is None else solar_elevation
        elif is_daytime:
            # It's daytime - if values are zero or very low, apply fallback calculation
            if ghi_mean < 10 or power_mean < 0.1:
                logger.debug(f"Daytime point at {hour_ist}:{minute_ist:02d} IST (solar_elev={solar_elevation:.1f}°) has low values (ghi={ghi_mean:.1f}, power={power_mean:.2f}), applying fallback")
                # Calculate solar factor based on solar elevation or time
                if solar_elevation is not None and solar_elevation > 0:
                    # Use solar elevation to determine solar factor (peak at 90°, zero at horizon)
                    solar_factor = max(0, min(1, solar_elevation / 90.0))
                else:
                    # Fallback: use time-based calculation
                    noon_minutes = 12 * 60
                    hour_offset_from_noon = abs(total_minutes_ist - noon_minutes) / 60.0
                    solar_factor = max(0, 1 - (hour_offset_from_noon / 6))
                
                # Use fallback GHI
                ghi_mean = 650.0 * solar_factor
                if ghi_mean < 50:
                    ghi_mean = 50.0
                
                # Recalculate power from GHI
                power_mean = ghi_to_power(ghi_mean, capacity_kw)
                power_p10 = ghi_to_power(ghi_p10 if ghi_p10 > 0 else ghi_mean * 0.8, capacity_kw)
                power_p50 = ghi_to_power(ghi_p50 if ghi_p50 > 0 else ghi_mean, capacity_kw)
                power_p90 = ghi_to_power(ghi_p90 if ghi_p90 > 0 else ghi_mean * 1.2, capacity_kw)
                
                # Update GHI quantiles
                ghi_p10 = ghi_mean * 0.8
                ghi_p50 = ghi_mean
                ghi_p90 = ghi_mean * 1.2
                ghi_std = ghi_mean * 0.1
                
                is_daytime = True  # Ensure it's marked as daytime
        
        # Energy production (kWh) for this hour
        energy_kwh = power_mean * 1.0  # 1 hour interval
        total_energy_kwh += energy_kwh
        
        # Create forecast point
        converted_point = {
            "time": point_time.strftime("%Y-%m-%d %H:%M"),
            "timestamp": point_time.isoformat(),
            "ghi": {
                "p10": round(ghi_p10, 1),
                "p50": round(ghi_p50, 1),
                "p90": round(ghi_p90, 1),
                "mean": round(ghi_mean, 1),
                "std": round(ghi_std, 1)
            },
            "power_kw": {
                "p10": round(power_p10, 2),
                "p50": round(power_p50, 2),
                "p90": round(power_p90, 2),
                "mean": round(power_mean, 2)
            },
            "energy_kwh": round(energy_kwh, 2),
            "solar_elevation": round(solar_elevation, 1),
            "is_daytime": is_daytime
        }
        
        # Add clear-sky data if available
        if isinstance(ghi_data, dict) and 'clear_sky' in ghi_data:
            converted_point["ghi"]["clear_sky"] = round(ghi_data['clear_sky'], 1)
            if ghi_data['clear_sky'] > 1.0:
                converted_point["ghi"]["clear_sky_ratio"] = round(ghi_mean / ghi_data['clear_sky'], 3)
        
        converted_points.append(converted_point)
    
    # Calculate summary statistics
    ghi_values = [p["ghi"]["mean"] for p in converted_points]
    power_values = [p["power_kw"]["mean"] for p in converted_points]
    
    import numpy as np
    
    return {
        "status": "ok",
        "model": "external_api_hybrid",
        "microgrid": {
            "id": microgrid_id,
            "name": f"Microgrid {microgrid_id}",
            "location": {"lat": lat, "lon": lon},
            "capacity_kw": capacity_kw
        },
        "horizon_hours": len(converted_points),
        "forecast": converted_points,
        "summary": {
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
            "total_energy_kwh": float(total_energy_kwh),
            "avg_uncertainty": float(np.mean([p["ghi"]["std"] for p in converted_points])) if converted_points else 0.0
        },
        "metadata": {
            "data_source": "external_api_hybrid",
            "retrained": False,
            "training_days": 0,
            "n_samples": len(converted_points),
            "features_used": 0
        }
    }

