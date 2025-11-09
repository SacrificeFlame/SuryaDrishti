from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request Models
class CurrentConditions(BaseModel):
    irradiance: float = Field(..., description="Current irradiance in W/m²")
    temperature: float = Field(..., description="Temperature in °C")
    humidity: float = Field(..., description="Humidity in %")
    wind_speed: Optional[float] = Field(None, description="Wind speed in m/s")

class ForecastRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 10
    current_conditions: CurrentConditions

# Response Models
class ForecastPoint(BaseModel):
    time: str
    timestamp: datetime
    p10: float = Field(..., description="10th percentile (pessimistic)")
    p50: float = Field(..., description="50th percentile (most likely)")
    p90: float = Field(..., description="90th percentile (optimistic)")
    power_output: float = Field(..., description="Expected power output in kW")

class CloudData(BaseModel):
    cloud_map: List[List[int]]
    motion_vectors: List[List[Dict[str, float]]]
    predicted_paths: Optional[List[List[Dict[str, Any]]]] = None

class AlertData(BaseModel):
    id: Optional[int] = None
    severity: str
    message: str
    timestamp: datetime
    action: Optional[str] = None

class ForecastResponse(BaseModel):
    location: Dict[str, float]
    timestamp: datetime
    forecasts: List[ForecastPoint]
    confidence: float
    alerts: List[AlertData]
    cloud_data: Optional[CloudData] = None
    current_irradiance: float
    current_power_output: float

# Microgrid Models
class MicrogridInfo(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    capacity_kw: float
    created_at: datetime

class SystemStatus(BaseModel):
    battery: Dict[str, float]  # {soc, voltage, current}
    diesel: Dict[str, Any]  # {status, fuelLevel}
    loads: Dict[str, float]  # {critical, nonCritical}
    timestamp: datetime
    recent_actions: List[Dict[str, Any]]
    uptime_hours: Optional[float] = None  # System uptime in hours

# Sensor Models
class SensorReadingRequest(BaseModel):
    microgrid_id: str
    irradiance: float
    power_output: float
    temperature: float
    humidity: float
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None

class SensorReadingResponse(BaseModel):
    id: int
    microgrid_id: str
    timestamp: datetime
    irradiance: float
    power_output: float
    temperature: float
    humidity: float
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None

# Alert Models
class AlertResponse(BaseModel):
    id: int
    microgrid_id: str
    timestamp: datetime
    severity: str
    message: str
    action_taken: Optional[str] = None
    resolved_at: Optional[datetime] = None
    acknowledged: bool

class AlertAcknowledge(BaseModel):
    acknowledged: bool = True

# Authentication Models
class UserRegister(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")

class UserLogin(BaseModel):
    email_or_username: str = Field(..., description="Email or username")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_verified: bool
    plan: str
    profile_picture: Optional[str] = None
    trial_start_date: Optional[str] = None  # ISO format string
    trial_end_date: Optional[str] = None  # ISO format string

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Device Management Models
class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    power_consumption_watts: float = Field(..., gt=0, description="Power consumption in watts")
    device_type: str = Field(..., description="Device type: essential, flexible, or optional")
    minimum_runtime_minutes: int = Field(0, ge=0, description="Minimum runtime in minutes")
    preferred_hours: Optional[Dict[str, int]] = Field(None, description="Preferred operating hours: {start: 8, end: 18}")
    priority_level: int = Field(3, ge=1, le=5, description="Priority level 1-5 (1 is highest)")

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    power_consumption_watts: Optional[float] = Field(None, gt=0)
    device_type: Optional[str] = None
    minimum_runtime_minutes: Optional[int] = Field(None, ge=0)
    preferred_hours: Optional[Dict[str, int]] = None
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None

class DeviceResponse(BaseModel):
    id: int
    microgrid_id: str
    name: str
    power_consumption_watts: float
    device_type: str
    minimum_runtime_minutes: int
    preferred_hours: Optional[Dict[str, int]] = None
    priority_level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Schedule Models
class ScheduleTimeSlot(BaseModel):
    time: str  # ISO format timestamp
    solar_generation_kw: float
    total_load_kw: float
    battery_charge_kw: float  # Positive = charging, negative = discharging
    battery_soc: float  # State of charge 0-1
    grid_import_kw: float  # Positive = importing from grid
    grid_export_kw: float  # Positive = exporting to grid (selling surplus)
    generator_power_kw: float  # Generator output
    devices: List[Dict[str, Any]]  # List of active devices in this slot

class ScheduleResponse(BaseModel):
    id: int
    microgrid_id: str
    date: datetime
    schedule_data: Dict[str, Any]  # Full schedule with time slots
    optimization_metrics: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ScheduleGenerateRequest(BaseModel):
    date: Optional[datetime] = Field(None, description="Date for schedule (defaults to today)")
    use_forecast: bool = Field(True, description="Use solar forecast data")
    optimization_mode: Optional[str] = Field(None, description="Override optimization mode")

# System Configuration Models
class SystemConfigurationUpdate(BaseModel):
    # Battery parameters
    battery_capacity_kwh: Optional[float] = Field(None, gt=0)
    battery_max_charge_rate_kw: Optional[float] = Field(None, gt=0)
    battery_max_discharge_rate_kw: Optional[float] = Field(None, gt=0)
    battery_efficiency: Optional[float] = Field(None, gt=0, le=1)
    battery_min_soc: Optional[float] = Field(None, ge=0, le=1)
    battery_max_soc: Optional[float] = Field(None, ge=0, le=1)
    
    # Grid pricing
    grid_peak_rate_per_kwh: Optional[float] = Field(None, ge=0)
    grid_off_peak_rate_per_kwh: Optional[float] = Field(None, ge=0)
    grid_peak_hours: Optional[Dict[str, int]] = None
    grid_export_rate_per_kwh: Optional[float] = Field(None, ge=0)
    grid_export_enabled: Optional[bool] = None
    
    # Generator specs
    generator_fuel_consumption_l_per_kwh: Optional[float] = Field(None, gt=0)
    generator_fuel_cost_per_liter: Optional[float] = Field(None, ge=0)
    generator_min_runtime_minutes: Optional[int] = Field(None, ge=0)
    generator_max_power_kw: Optional[float] = Field(None, gt=0)
    
    # Optimization preferences
    optimization_mode: Optional[str] = None
    safety_margin_critical_loads: Optional[float] = Field(None, ge=0, le=1)

class SystemConfigurationResponse(BaseModel):
    id: int
    microgrid_id: str
    battery_capacity_kwh: float
    battery_max_charge_rate_kw: float
    battery_max_discharge_rate_kw: float
    battery_efficiency: float
    battery_min_soc: float
    battery_max_soc: float
    grid_peak_rate_per_kwh: float
    grid_off_peak_rate_per_kwh: float
    grid_peak_hours: Optional[Dict[str, int]] = None
    grid_export_rate_per_kwh: float
    grid_export_enabled: bool
    generator_fuel_consumption_l_per_kwh: float
    generator_fuel_cost_per_liter: float
    generator_min_runtime_minutes: int
    generator_max_power_kw: float
    optimization_mode: str
    safety_margin_critical_loads: float
    created_at: datetime
    updated_at: datetime

# Optimization Metrics
class OptimizationMetrics(BaseModel):
    solar_utilization_percent: float
    grid_import_reduction_percent: float
    estimated_cost_savings: float
    battery_cycle_efficiency: float
    carbon_footprint_reduction_kg: float
    generator_runtime_minutes: float
    total_energy_kwh: float
    solar_energy_kwh: float
    grid_energy_kwh: float
    grid_export_energy_kwh: float
    grid_export_revenue: float
    battery_energy_kwh: float
    generator_energy_kwh: float


