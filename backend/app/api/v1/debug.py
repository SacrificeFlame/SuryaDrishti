"""
Debug endpoints for troubleshooting API issues.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from app.services.external_forecast_service import (
    EXTERNAL_API_URL, 
    EXTERNAL_API_KEY, 
    get_external_api_url_with_bypass
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/test-external-api")
async def test_external_api():
    """
    Test the external API connection and return detailed response.
    Useful for debugging API connection issues.
    """
    try:
        # Use URL with bypass parameter (more reliable)
        api_url = get_external_api_url_with_bypass()
        logger.info(f"Testing external API: {api_url}")
        logger.info(f"Original URL: {EXTERNAL_API_URL}")
        logger.info(f"URL with bypass: {api_url}")
        logger.info(f"Bypass in URL: {'ngrok-skip-browser-warning' in api_url}")
        
        async with httpx.AsyncClient(timeout=35.0, follow_redirects=True) as client:
            # Prepare headers with ngrok bypass
            request_headers = {
                "Content-Type": "application/json",
                "x-api-key": EXTERNAL_API_KEY,
                "User-Agent": "SuryaDrishti-Backend/1.0",
                "ngrok-skip-browser-warning": "true",  # Bypass ngrok browser warning (header)
            }
            
            logger.info(f"Sending request with headers: {list(request_headers.keys())}")
            logger.info(f"URL includes bypass parameter: {'ngrok-skip-browser-warning' in api_url}")
            
            response = await client.post(
                api_url,  # URL with bypass parameter
                headers=request_headers,  # Headers with bypass header
                json={"source": "hybrid"},
            )
            
            # Get response details
            try:
                response_text = response.text[:2000]  # First 2000 chars
            except:
                response_text = "Could not read response text"
            
            try:
                response_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            except:
                response_json = None
            
            return JSONResponse(
                content={
                    "status": "success" if response.status_code == 200 else "error",
                    "request": {
                        "url": api_url,
                        "original_url": EXTERNAL_API_URL,
                        "url_has_bypass": "ngrok-skip-browser-warning" in api_url,
                        "method": "POST",
                        "headers": {
                            "Content-Type": "application/json",
                            "x-api-key": EXTERNAL_API_KEY[:10] + "..." if len(EXTERNAL_API_KEY) > 10 else EXTERNAL_API_KEY,
                            "User-Agent": "SuryaDrishti-Backend/1.0",
                            "ngrok-skip-browser-warning": "true",
                        },
                        "body": {"source": "hybrid"}
                    },
                    "response": {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "text": response_text,
                        "json": response_json,
                        "url": str(response.url),
                    },
                    "diagnosis": {
                        "connection": "ok" if response.status_code else "failed",
                        "api_responded": True,
                        "status_ok": response.status_code == 200,
                        "content_type": response.headers.get("content-type", "unknown"),
                        "bypass_applied": "ngrok-skip-browser-warning" in api_url,
                    }
                },
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
    except httpx.TimeoutException as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": {
                    "type": "timeout",
                    "message": "Request timed out after 35 seconds",
                    "url": api_url if 'api_url' in locals() else EXTERNAL_API_URL
                },
                "diagnosis": {
                    "connection": "timeout",
                    "api_responded": False,
                }
            },
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except httpx.ConnectError as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": {
                    "type": "connection_error",
                    "message": str(e),
                    "url": api_url if 'api_url' in locals() else EXTERNAL_API_URL
                },
                "diagnosis": {
                    "connection": "failed",
                    "api_responded": False,
                    "possible_causes": [
                        "ngrok URL is down or expired",
                        "Network connectivity issue",
                        "API server is not running"
                    ]
                }
            },
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "error": {
                    "type": "exception",
                    "message": str(e),
                    "error_type": type(e).__name__
                },
                "diagnosis": {
                    "connection": "unknown_error",
                    "api_responded": False,
                },
                "code_info": {
                    "bypass_function_exists": hasattr(get_external_api_url_with_bypass, '__call__'),
                    "original_url": EXTERNAL_API_URL,
                }
            },
            status_code=200,
            headers={"Access-Control-Allow-Origin": "*"}
        )


@router.get("/api-config")
async def get_api_config():
    """
    Get current API configuration (without sensitive keys).
    """
    api_url_with_bypass = get_external_api_url_with_bypass()
    return JSONResponse(
        content={
            "external_api_url": EXTERNAL_API_URL,
            "external_api_url_with_bypass": api_url_with_bypass,
            "bypass_applied": "ngrok-skip-browser-warning" in api_url_with_bypass,
            "api_key_length": len(EXTERNAL_API_KEY),
            "api_key_preview": EXTERNAL_API_KEY[:10] + "..." if len(EXTERNAL_API_KEY) > 10 else "***",
            "timeout_seconds": 35,
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )


@router.get("/check-code-version")
async def check_code_version():
    """
    Check if the bypass code is loaded and working.
    """
    try:
        api_url = get_external_api_url_with_bypass()
        return JSONResponse(
            content={
                "status": "ok",
                "code_loaded": True,
                "original_url": EXTERNAL_API_URL,
                "url_with_bypass": api_url,
                "bypass_in_url": "ngrok-skip-browser-warning" in api_url,
                "message": "✅ Code is loaded correctly. If URL still doesn't have bypass, server needs restart."
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "code_loaded": False,
                "error": str(e),
                "message": "❌ Code not loaded - check if server was restarted"
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )


@router.post("/validate-forecast")
async def validate_forecast(forecast_data: Dict):
    """
    Validate if a solar irradiance and power forecast is realistic.
    
    Accepts forecast data in the format returned by /api/v1/forecast/microgrid/{id}
    or /api/v1/forecast/ngboost endpoints.
    
    Returns:
    - Verdict: "realistic", "optimistic", or "incorrect"
    - Detailed analysis
    - Possible causes for any issues
    """
    try:
        issues: List[str] = []
        warnings: List[str] = []
        checks_passed: List[str] = []
        
        # Extract forecast points
        forecast_points = forecast_data.get("forecast", [])
        if not forecast_points:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "No forecast data provided"
                },
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Extract location and capacity
        location = forecast_data.get("microgrid", {}).get("location") or forecast_data.get("location", {})
        lat = location.get("lat")
        lon = location.get("lon")
        capacity_kw = forecast_data.get("microgrid", {}).get("capacity_kw")
        
        # Extract summary statistics
        summary = forecast_data.get("summary", {})
        ghi_summary = summary.get("ghi", {})
        power_summary = summary.get("power_kw", {})
        
        max_ghi = ghi_summary.get("max", 0)
        mean_ghi = ghi_summary.get("mean", 0)
        max_power = power_summary.get("max", 0)
        mean_power = power_summary.get("mean", 0)
        
        # Check 1: Peak GHI values
        if max_ghi > 1000:
            issues.append(f"Peak GHI ({max_ghi:.1f} W/m²) exceeds physical maximum (~1000 W/m²)")
        elif max_ghi > 900:
            warnings.append(f"Peak GHI ({max_ghi:.1f} W/m²) is very high - verify clear-sky conditions")
        elif max_ghi > 0:
            checks_passed.append(f"Peak GHI ({max_ghi:.1f} W/m²) is within reasonable range")
        
        # Check 2: Capacity factor
        if capacity_kw and capacity_kw > 0:
            peak_cf = (max_power / capacity_kw * 100) if max_power > 0 else 0
            avg_cf = (mean_power / capacity_kw * 100) if mean_power > 0 else 0
            
            if peak_cf > 85:
                issues.append(f"Peak capacity factor ({peak_cf:.1f}%) is unrealistically high (>85%)")
            elif peak_cf > 75:
                warnings.append(f"Peak capacity factor ({peak_cf:.1f}%) is high - verify site conditions")
            elif peak_cf > 0:
                checks_passed.append(f"Peak capacity factor ({peak_cf:.1f}%) is realistic")
            
            if avg_cf > 40:
                warnings.append(f"Average capacity factor ({avg_cf:.1f}%) is high for horizontal panels")
            elif avg_cf > 0:
                checks_passed.append(f"Average capacity factor ({avg_cf:.1f}%) is reasonable")
        
        # Check 3: Clear-sky comparison
        clear_sky_ratios = []
        solar_elevations = []
        daytime_points = 0
        
        for point in forecast_points:
            ghi_data = point.get("ghi", {})
            ghi_mean = ghi_data.get("mean", 0)
            ghi_clear = ghi_data.get("clear_sky")
            solar_elev = point.get("solar_elevation")
            is_daytime = point.get("is_daytime", False)
            
            if is_daytime:
                daytime_points += 1
            
            if solar_elev is not None:
                solar_elevations.append(solar_elev)
            
            if ghi_clear and ghi_clear > 10 and ghi_mean > 0:
                ratio = ghi_mean / ghi_clear
                clear_sky_ratios.append(ratio)
                if ratio > 1.15:
                    issues.append(f"Forecast GHI ({ghi_mean:.1f} W/m²) exceeds clear-sky ({ghi_clear:.1f} W/m²) by >15%")
                elif ratio > 1.10:
                    warnings.append(f"Forecast GHI ({ghi_mean:.1f} W/m²) exceeds clear-sky ({ghi_clear:.1f} W/m²) by >10%")
        
        if clear_sky_ratios:
            avg_ratio = np.mean(clear_sky_ratios)
            if avg_ratio > 1.10:
                issues.append(f"Average clear-sky ratio ({avg_ratio:.2f}) indicates overly optimistic forecasts")
            elif avg_ratio < 0.3:
                warnings.append(f"Average clear-sky ratio ({avg_ratio:.2f}) is very low - heavy cloud cover expected")
            else:
                checks_passed.append(f"Clear-sky ratio ({avg_ratio:.2f}) is reasonable")
        
        # Check 4: Solar elevation vs GHI
        if solar_elevations:
            max_elev = max(solar_elevations)
            min_elev = min([e for e in solar_elevations if e > -5]) if any(e > -5 for e in solar_elevations) else 0
            
            # Find GHI at max elevation
            max_ghi_at_max_elev = 0
            for point in forecast_points:
                if abs(point.get("solar_elevation", 0) - max_elev) < 1:
                    max_ghi_at_max_elev = max(max_ghi_at_max_elev, point.get("ghi", {}).get("mean", 0))
            
            # Expected GHI scales roughly with sin(elevation)
            # At 90° elevation, max ~1000 W/m²; at 30°, max ~500 W/m²
            if max_elev > 0:
                expected_max = 1000 * np.sin(np.radians(max_elev))
                if max_ghi_at_max_elev > expected_max * 1.2:
                    issues.append(f"GHI at max elevation ({max_elev:.1f}°) exceeds expected ({expected_max:.0f} W/m²)")
        
        # Check 5: Daytime detection
        if daytime_points == 0 and len(forecast_points) > 0:
            # Check if any points should be daytime
            for point in forecast_points[:5]:  # Check first 5 points
                time_str = point.get("time", "")
                hour = int(time_str.split(":")[0].split()[-1]) if ":" in time_str else None
                if hour and 6 <= hour < 19:
                    issues.append(f"Point at {time_str} should be daytime but marked as nighttime")
                    break
        
        # Check 6: Power conversion consistency
        if capacity_kw and capacity_kw > 0:
            # Expected efficiency: ~77% (0.85 * 0.95 * 0.95 * 0.97)
            expected_efficiency = 0.77
            for point in forecast_points[:10]:  # Check first 10 points
                ghi_mean = point.get("ghi", {}).get("mean", 0)
                power_mean = point.get("power_kw", {}).get("mean", 0) if "power_kw" in point else None
                
                if power_mean is not None and ghi_mean > 10:
                    # Calculate expected power
                    expected_power = (ghi_mean / 1000.0) * capacity_kw * expected_efficiency
                    actual_efficiency = (power_mean / capacity_kw) / (ghi_mean / 1000.0) if ghi_mean > 0 else 0
                    
                    if abs(actual_efficiency - expected_efficiency) > 0.15:  # More than 15% difference
                        warnings.append(f"Power conversion efficiency ({actual_efficiency:.2%}) differs from expected ({expected_efficiency:.2%})")
                        break
        
        # Determine verdict
        if len(issues) > 0:
            verdict = "incorrect"
            severity = "high"
        elif len(warnings) >= 2:
            verdict = "optimistic"
            severity = "medium"
        elif len(warnings) == 1:
            verdict = "mostly realistic"
            severity = "low"
        else:
            verdict = "realistic"
            severity = "none"
        
        # Possible causes
        possible_causes = []
        if max_ghi > 900:
            possible_causes.append("Model may be overestimating clear-sky conditions")
        if capacity_kw and (max_power / capacity_kw) > 0.80:
            possible_causes.append("Loss factors (temperature, pollution, soiling) may be underestimated")
        if clear_sky_ratios and np.mean(clear_sky_ratios) > 1.10:
            possible_causes.append("Forecast exceeds clear-sky model - check for data leakage or model calibration issues")
        if daytime_points == 0 and len(forecast_points) > 5:
            possible_causes.append("Daytime detection may be incorrectly marking all points as nighttime")
        if not possible_causes:
            possible_causes.append("No significant issues detected")
        
        return JSONResponse(
            content={
                "status": "ok",
                "verdict": verdict,
                "severity": severity,
                "summary": {
                    "total_points": len(forecast_points),
                    "daytime_points": daytime_points,
                    "max_ghi_w_m2": float(max_ghi),
                    "mean_ghi_w_m2": float(mean_ghi),
                    "max_power_kw": float(max_power),
                    "mean_power_kw": float(mean_power),
                    "peak_capacity_factor_percent": float((max_power / capacity_kw * 100) if capacity_kw and capacity_kw > 0 else 0),
                    "avg_clear_sky_ratio": float(np.mean(clear_sky_ratios)) if clear_sky_ratios else None,
                },
                "checks": {
                    "passed": checks_passed,
                    "warnings": warnings,
                    "issues": issues
                },
                "possible_causes": possible_causes[:3],  # Top 3 causes
                "recommendations": [
                    "Compare with historical data for the same location and time",
                    "Verify clear-sky GHI calculations using pvlib",
                    "Check if loss factors match local conditions (pollution, temperature, soiling)",
                    "Validate solar elevation calculations",
                    "Review model training data for potential data leakage"
                ] if len(issues) > 0 or len(warnings) > 0 else [
                    "Forecast appears realistic - proceed with confidence"
                ]
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )
        
    except Exception as e:
        logger.error(f"Error validating forecast: {e}", exc_info=True)
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Validation failed: {str(e)}"
            },
            headers={"Access-Control-Allow-Origin": "*"}
        )
