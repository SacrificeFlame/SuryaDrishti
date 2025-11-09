from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    plan = Column(String, default='trial')  # trial, starter, professional, enterprise
    trial_start_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    profile_picture = Column(String, nullable=True)  # Path or URL to profile picture
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Microgrid(Base):
    __tablename__ = "microgrids"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity_kw = Column(Float, nullable=False)
    contact_phone = Column(String, nullable=True)  # Phone number for SMS notifications
    contact_email = Column(String, nullable=True)  # Email for notifications
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    forecasts = relationship("Forecast", back_populates="microgrid")
    sensor_readings = relationship("SensorReading", back_populates="microgrid")
    alerts = relationship("Alert", back_populates="microgrid")
    notification_preferences = relationship("NotificationPreference", back_populates="microgrid")

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Forecast data (JSON format for flexibility)
    predictions = Column(JSON)  # {5min: {p10, p50, p90}, 10min: {...}, ...}
    cloud_data = Column(JSON)   # Cloud map and motion vectors
    confidence_score = Column(Float)
    
    # Actual outcome (for validation)
    actual_irradiance = Column(Float, nullable=True)
    actual_power_output = Column(Float, nullable=True)
    
    microgrid = relationship("Microgrid", back_populates="forecasts")

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Measurements
    irradiance = Column(Float)  # W/m²
    power_output = Column(Float)  # kW
    temperature = Column(Float)  # °C
    humidity = Column(Float)  # %
    wind_speed = Column(Float)  # m/s
    wind_direction = Column(Float, nullable=True)  # degrees
    
    microgrid = relationship("Microgrid", back_populates="sensor_readings")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String)  # 'info', 'warning', 'critical'
    message = Column(Text)
    action_taken = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged = Column(Integer, default=0)  # 0 or 1 for SQLite compatibility
    
    microgrid = relationship("Microgrid", back_populates="alerts")

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    power_consumption_watts = Column(Float, nullable=False)  # Power in watts
    device_type = Column(String, nullable=False)  # 'essential', 'flexible', 'optional'
    minimum_runtime_minutes = Column(Integer, default=0)  # Minimum runtime in minutes
    preferred_hours = Column(JSON, nullable=True)  # e.g., {"start": 8, "end": 18} in 24h format
    priority_level = Column(Integer, default=3)  # 1-5, where 1 is highest priority
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    microgrid = relationship("Microgrid")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # Date for which schedule is generated
    schedule_data = Column(JSON, nullable=False)  # Full schedule with time slots
    optimization_metrics = Column(JSON, nullable=True)  # Metrics from optimization
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    microgrid = relationship("Microgrid")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"), nullable=False, index=True)
    phone_number = Column(String, nullable=True)  # E.164 format
    email = Column(String, nullable=True)
    enable_sms = Column(Boolean, default=True)
    enable_email = Column(Boolean, default=False)
    enable_critical_alerts = Column(Boolean, default=True)
    enable_warning_alerts = Column(Boolean, default=True)
    enable_info_alerts = Column(Boolean, default=False)
    enable_forecast_updates = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    microgrid = relationship("Microgrid", back_populates="notification_preferences")

class SystemConfiguration(Base):
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    microgrid_id = Column(String, ForeignKey("microgrids.id"), nullable=False, unique=True, index=True)
    
    # Battery parameters
    battery_capacity_kwh = Column(Float, default=50.0)  # Battery capacity in kWh
    battery_max_charge_rate_kw = Column(Float, default=10.0)  # Max charge rate in kW
    battery_max_discharge_rate_kw = Column(Float, default=10.0)  # Max discharge rate in kW
    battery_efficiency = Column(Float, default=0.95)  # Round-trip efficiency (0-1)
    battery_min_soc = Column(Float, default=0.2)  # Minimum SOC (0-1)
    battery_max_soc = Column(Float, default=0.95)  # Maximum SOC (0-1)
    
    # Grid pricing
    grid_peak_rate_per_kwh = Column(Float, default=10.0)  # Peak rate in currency per kWh
    grid_off_peak_rate_per_kwh = Column(Float, default=5.0)  # Off-peak rate
    grid_peak_hours = Column(JSON, nullable=True)  # e.g., {"start": 8, "end": 20}
    grid_export_rate_per_kwh = Column(Float, default=4.0)  # Rate for selling excess to grid (feed-in tariff)
    grid_export_enabled = Column(Boolean, default=True)  # Enable/disable grid export
    
    # Generator specs
    generator_fuel_consumption_l_per_kwh = Column(Float, default=0.25)  # Liters per kWh
    generator_fuel_cost_per_liter = Column(Float, default=80.0)  # Cost per liter
    generator_min_runtime_minutes = Column(Integer, default=30)  # Minimum runtime
    generator_max_power_kw = Column(Float, default=20.0)  # Max generator power
    
    # Optimization preferences
    optimization_mode = Column(String, default='cost')  # 'cost', 'battery_longevity', 'grid_independence'
    safety_margin_critical_loads = Column(Float, default=0.1)  # 10% safety margin
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    microgrid = relationship("Microgrid")


