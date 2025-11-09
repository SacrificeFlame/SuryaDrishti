"""
Forecast Validation Utility
Validates solar irradiance and power forecasts for physical realism.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from app.utils.physics import calculate_solar_zenith, calculate_clear_sky_irradiance


def validate_forecast_realism(
    forecast_data: List[Dict],
    latitude: float,
    longitude: float,
    capacity_kw: float,
    location_name: str = "Unknown"
) -> Dict:
    """
    Validate if a solar irradiance and power forecast is realistic.
    
    Args:
        forecast_data: List of forecast points with keys:
            - timestamp (ISO string or datetime)
            - ghi (dict with mean, p10, p50, p90) or direct value
            - power_kw (dict with mean) or direct value
            - solar_elevation (optional)
        latitude: Location latitude
        longitude: Location longitude
        capacity_kw: System capacity in kW
        location_name: Name of location for reporting
        
    Returns:
        Dictionary with validation results, verdict, and causes
    """
    issues = []
    warnings = []
    realistic_count = 0
    total_count = 0
    
    # Expected values based on location and time
    max_ghi_expected = 1000.0  # W/m² - Delhi/India peak
    if abs(latitude) < 10:
        max_ghi_expected = 1100.0  # Equatorial regions
    elif abs(latitude) > 30:
        max_ghi_expected = 900.0  # Higher latitude regions
    
    realistic_capacity_factor_peak = 0.75  # 75% peak is realistic
    realistic_capacity_factor_avg = 0.30  # 30% average is realistic
    
    max_power_expected = capacity_kw * realistic_capacity_factor_peak
    
    # Track statistics
    ghi_values = []
    power_values = []
    capacity_factors = []
    clear_sky_ratios = []
    
    for point in forecast_data:
        total_count += 1
        
        # Parse timestamp
        timestamp = point.get('timestamp')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.utcnow()
        
        if not isinstance(timestamp, datetime):
            timestamp = datetime.utcnow()
        
        hour = timestamp.hour
        minute = timestamp.minute
        
        # Get GHI value
        ghi_data = point.get('ghi', {})
        if isinstance(ghi_data, dict):
            ghi_mean = ghi_data.get('mean', ghi_data.get('p50', 0))
        else:
            ghi_mean = float(ghi_data) if ghi_data else 0
        
        # Get power value
        power_data = point.get('power_kw', {})
        if isinstance(power_data, dict):
            power_mean = power_data.get('mean', power_data.get('p50', 0))
        else:
            power_mean = float(power_data) if power_data else 0
        
        # Get solar elevation
        solar_elevation = point.get('solar_elevation')
        if solar_elevation is None:
            # Calculate solar elevation
            zenith = calculate_solar_zenith(latitude, longitude, timestamp)
            solar_elevation = 90 - zenith
        
        # Check if daytime
        is_daytime = point.get('is_daytime')
        if is_daytime is None:
            is_daytime = 6 <= hour < 19  # Rough daytime check
        
        # Calculate clear-sky GHI for comparison
        zenith = calculate_solar_zenith(latitude, longitude, timestamp)
        clear_sky_ghi = calculate_clear_sky_irradiance(zenith)
        
        # Validation checks
        point_issues = []
        point_warnings = []
        
        # 1. Check for negative values
        if ghi_mean < 0:
            point_issues.append(f"Negative GHI value: {ghi_mean:.2f} W/m² at {hour:02d}:{minute:02d}")
        if power_mean < 0:
            point_issues.append(f"Negative power value: {power_mean:.2f} kW at {hour:02d}:{minute:02d}")
        
        # 2. Nighttime checks
        if not is_daytime or solar_elevation < 0:
            if ghi_mean > 10:
                point_issues.append(f"High GHI at night: {ghi_mean:.2f} W/m² at {hour:02d}:{minute:02d} (elevation: {solar_elevation:.1f}°)")
            if power_mean > 0.1 * capacity_kw:
                point_issues.append(f"High power at night: {power_mean:.2f} kW at {hour:02d}:{minute:02d}")
        else:
            # Daytime checks
            # 3. Check GHI against clear-sky
            if clear_sky_ghi > 10:  # Only check if meaningful clear-sky value
                clear_sky_ratio = ghi_mean / clear_sky_ghi
                clear_sky_ratios.append(clear_sky_ratio)
                
                if clear_sky_ratio > 1.15:
                    point_issues.append(
                        f"GHI exceeds clear-sky by {((clear_sky_ratio-1)*100):.1f}%: "
                        f"{ghi_mean:.1f} vs {clear_sky_ghi:.1f} W/m² at {hour:02d}:{minute:02d}"
                    )
                elif clear_sky_ratio > 1.05:
                    point_warnings.append(
                        f"GHI slightly above clear-sky: {ghi_mean:.1f} vs {clear_sky_ghi:.1f} W/m²"
                    )
            
            # 4. Check GHI against maximum expected
            if ghi_mean > max_ghi_expected:
                point_issues.append(
                    f"GHI exceeds maximum expected ({max_ghi_expected} W/m²): "
                    f"{ghi_mean:.1f} W/m² at {hour:02d}:{minute:02d}"
                )
            
            # 5. Check power against capacity
            capacity_factor = power_mean / capacity_kw if capacity_kw > 0 else 0
            capacity_factors.append(capacity_factor)
            
            if capacity_factor > 0.85:
                point_issues.append(
                    f"Capacity factor too high ({capacity_factor*100:.1f}%): "
                    f"{power_mean:.2f} kW from {capacity_kw} kW system at {hour:02d}:{minute:02d}"
                )
            elif capacity_factor > 0.75:
                point_warnings.append(
                    f"High capacity factor: {capacity_factor*100:.1f}%"
                )
            
            # 6. Check power against expected from GHI
            # Expected power = (GHI/1000) * capacity * efficiency
            # With realistic losses: ~77% efficiency
            expected_power = (ghi_mean / 1000.0) * capacity_kw * 0.77
            power_ratio = power_mean / expected_power if expected_power > 0.1 else 0
            
            if expected_power > 0.1:  # Only check if meaningful
                if power_ratio > 1.2:
                    point_issues.append(
                        f"Power exceeds expected from GHI: "
                        f"{power_mean:.2f} kW vs {expected_power:.2f} kW expected "
                        f"(ratio: {power_ratio:.2f}) at {hour:02d}:{minute:02d}"
                    )
                elif power_ratio < 0.5 and ghi_mean > 200:
                    point_warnings.append(
                        f"Power lower than expected from GHI: "
                        f"{power_mean:.2f} kW vs {expected_power:.2f} kW expected"
                    )
        
        # 7. Check solar elevation constraints
        if is_daytime and solar_elevation > 0:
            # At low elevation, GHI should be limited
            max_ghi_at_elevation = max_ghi_expected * np.sin(np.radians(solar_elevation))
            if ghi_mean > max_ghi_at_elevation * 1.2:
                point_warnings.append(
                    f"GHI high for solar elevation {solar_elevation:.1f}°: "
                    f"{ghi_mean:.1f} W/m² (max expected: {max_ghi_at_elevation:.1f} W/m²)"
                )
        
        if len(point_issues) == 0:
            realistic_count += 1
        
        issues.extend(point_issues)
        warnings.extend(point_warnings)
        
        # Store values for statistics
        if is_daytime and solar_elevation > 5:
            ghi_values.append(ghi_mean)
            power_values.append(power_mean)
    
    # Calculate statistics
    stats = {
        'total_points': total_count,
        'realistic_points': realistic_count,
        'realism_percentage': (realistic_count / total_count * 100) if total_count > 0 else 0,
        'max_ghi': max(ghi_values) if ghi_values else 0,
        'avg_ghi': np.mean(ghi_values) if ghi_values else 0,
        'max_power': max(power_values) if power_values else 0,
        'avg_power': np.mean(power_values) if power_values else 0,
        'max_capacity_factor': max(capacity_factors) * 100 if capacity_factors else 0,
        'avg_capacity_factor': np.mean(capacity_factors) * 100 if capacity_factors else 0,
        'avg_clear_sky_ratio': np.mean(clear_sky_ratios) if clear_sky_ratios else 0,
    }
    
    # Determine verdict
    verdict = "realistic"
    causes = []
    
    if len(issues) > total_count * 0.1:  # More than 10% of points have issues
        verdict = "incorrect"
        causes.append("Multiple data points violate physical constraints")
    elif len(issues) > 0:
        verdict = "optimistic"
        causes.append("Some values exceed realistic bounds")
    elif len(warnings) > total_count * 0.2:  # More than 20% warnings
        verdict = "optimistic"
        causes.append("Many values at upper limits of realism")
    
    # Add specific causes based on issues
    if any("exceeds clear-sky" in issue for issue in issues):
        causes.append("GHI values exceed clear-sky irradiance (physically impossible)")
    
    if any("Capacity factor too high" in issue for issue in issues):
        causes.append("Power output exceeds realistic capacity factors (>85%)")
    
    if any("exceeds maximum expected" in issue for issue in issues):
        causes.append("GHI values exceed location-specific maximums")
    
    if stats['max_capacity_factor'] > 80:
        if "Capacity factor" not in str(causes):
            causes.append(f"Peak capacity factor ({stats['max_capacity_factor']:.1f}%) is very high for this location")
    
    if stats['avg_clear_sky_ratio'] > 1.05 and len(clear_sky_ratios) > 0:
        causes.append(f"Average GHI ({stats['avg_clear_sky_ratio']:.2f}x clear-sky) suggests overestimation")
    
    # Default causes if none identified
    if len(causes) == 0:
        if verdict == "realistic":
            causes.append("Values are within expected physical bounds")
        else:
            causes.append("Model may be overestimating solar resource")
            causes.append("Missing loss factors in power conversion")
    
    return {
        'verdict': verdict,
        'location': location_name,
        'coordinates': {'lat': latitude, 'lon': longitude},
        'capacity_kw': capacity_kw,
        'statistics': stats,
        'issues': issues[:10],  # Limit to first 10 issues
        'warnings': warnings[:10],  # Limit to first 10 warnings
        'total_issues': len(issues),
        'total_warnings': len(warnings),
        'possible_causes': causes[:3],  # Top 3 causes
        'recommendations': _generate_recommendations(verdict, issues, stats)
    }


def _generate_recommendations(verdict: str, issues: List[str], stats: Dict) -> List[str]:
    """Generate recommendations based on validation results."""
    recommendations = []
    
    if verdict == "incorrect":
        recommendations.append("Review forecast model - multiple physical constraints violated")
        recommendations.append("Check data preprocessing and feature engineering")
        recommendations.append("Validate against ground truth measurements if available")
    elif verdict == "optimistic":
        recommendations.append("Apply additional loss factors (temperature, soiling, pollution)")
        recommendations.append("Cap GHI values at clear-sky irradiance")
        recommendations.append("Reduce capacity factor expectations to 60-75% peak")
    else:
        recommendations.append("Forecast appears realistic - continue monitoring")
        recommendations.append("Consider site-specific calibration for improved accuracy")
    
    if stats.get('max_capacity_factor', 0) > 80:
        recommendations.append("Reduce power conversion efficiency assumptions")
    
    if stats.get('avg_clear_sky_ratio', 0) > 1.0:
        recommendations.append("Ensure GHI values do not exceed clear-sky model predictions")
    
    return recommendations

