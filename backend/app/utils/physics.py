import numpy as np
from datetime import datetime
import math

def calculate_solar_zenith(latitude: float, longitude: float, timestamp: datetime = None) -> float:
    """
    Calculate solar zenith angle for given location and time.
    
    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        timestamp: Datetime object (defaults to now)
    
    Returns:
        zenith_angle: Solar zenith angle in radians
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Convert to radians
    lat_rad = math.radians(latitude)
    
    # Day of year
    day_of_year = timestamp.timetuple().tm_yday
    
    # Solar declination (simplified)
    declination = math.radians(23.45) * math.sin(math.radians(360 * (day_of_year + 284) / 365))
    
    # Hour angle
    hour = timestamp.hour + timestamp.minute / 60.0
    hour_angle = math.radians(15 * (hour - 12))
    
    # Solar zenith angle
    cos_zenith = (math.sin(lat_rad) * math.sin(declination) + 
                  math.cos(lat_rad) * math.cos(declination) * math.cos(hour_angle))
    
    zenith = math.acos(max(-1, min(1, cos_zenith)))  # Clamp to valid range
    
    return zenith

def calculate_clear_sky_irradiance(zenith_angle: float, altitude: float = 0) -> float:
    """
    Calculate clear-sky irradiance using simplified model.
    
    Args:
        zenith_angle: Solar zenith angle in radians
        altitude: Altitude above sea level in meters
    
    Returns:
        irradiance: Clear-sky irradiance in W/m²
    """
    I0 = 1367  # Solar constant W/m²
    
    # Air mass
    if math.cos(zenith_angle) > 0:
        air_mass = 1 / math.cos(zenith_angle)
    else:
        return 0.0
    
    # Altitude correction
    altitude_factor = math.exp(altitude / 8500)  # Scale height ~8.5 km
    
    # Atmospheric attenuation
    tau = 0.15  # Optical depth
    irradiance = I0 * math.cos(zenith_angle) * math.exp(-tau * air_mass) * altitude_factor
    
    return max(0, irradiance)

def calculate_cloud_attenuation(cloud_opacity: int, cloud_type: str = 'thin') -> float:
    """
    Calculate irradiance attenuation factor due to clouds.
    
    Args:
        cloud_opacity: 0-3 (clear, thin, thick, storm)
        cloud_type: Type of cloud
    
    Returns:
        attenuation_factor: Multiplier for irradiance (0-1)
    """
    attenuation_map = {
        0: 1.0,    # Clear sky
        1: 0.7,    # Thin clouds
        2: 0.3,    # Thick clouds
        3: 0.1     # Storm clouds
    }
    
    return attenuation_map.get(cloud_opacity, 1.0)

def calculate_panel_efficiency(temperature: float, irradiance: float) -> float:
    """
    Calculate solar panel efficiency based on temperature and irradiance.
    
    Args:
        temperature: Panel temperature in °C
        irradiance: Solar irradiance in W/m²
    
    Returns:
        efficiency: Panel efficiency (0-1)
    """
    # Base efficiency at 25°C
    base_efficiency = 0.18  # 18% typical for silicon panels
    
    # Temperature coefficient (-0.4% per °C above 25°C)
    temp_coefficient = -0.004
    temp_loss = temp_coefficient * (temperature - 25)
    
    # Low irradiance loss
    if irradiance < 200:
        irradiance_factor = irradiance / 200 * 0.9
    else:
        irradiance_factor = 1.0
    
    efficiency = base_efficiency * (1 + temp_loss) * irradiance_factor
    
    return max(0, min(efficiency, 0.22))  # Clamp between 0 and 22%

def calculate_power_output(irradiance: float, panel_area: float, 
                          temperature: float, capacity_kw: float) -> float:
    """
    Calculate expected power output from solar panels.
    
    Args:
        irradiance: Solar irradiance in W/m²
        panel_area: Total panel area in m²
        temperature: Panel temperature in °C
        capacity_kw: Rated capacity in kW
    
    Returns:
        power_output: Power output in kW
    """
    efficiency = calculate_panel_efficiency(temperature, irradiance)
    
    # Power = Irradiance * Area * Efficiency
    power_w = irradiance * panel_area * efficiency
    power_kw = power_w / 1000
    
    # Cap at rated capacity
    return min(power_kw, capacity_kw)

def estimate_cloud_distance(cloud_position: tuple, microgrid_position: tuple) -> float:
    """
    Estimate distance to cloud in kilometers using haversine formula.
    
    Args:
        cloud_position: (lat, lon) of cloud center
        microgrid_position: (lat, lon) of microgrid
    
    Returns:
        distance: Distance in km
    """
    lat1, lon1 = math.radians(cloud_position[0]), math.radians(cloud_position[1])
    lat2, lon2 = math.radians(microgrid_position[0]), math.radians(microgrid_position[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in km
    r = 6371
    
    return c * r

def time_to_arrival(distance_km: float, velocity_m_per_s: float) -> float:
    """
    Calculate time for cloud to reach microgrid.
    
    Args:
        distance_km: Distance in kilometers
        velocity_m_per_s: Cloud velocity in m/s
    
    Returns:
        time_minutes: Time to arrival in minutes
    """
    if velocity_m_per_s <= 0:
        return float('inf')
    
    time_seconds = (distance_km * 1000) / velocity_m_per_s
    return time_seconds / 60


