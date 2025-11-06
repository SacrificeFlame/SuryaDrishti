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


