from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Microgrid(Base):
    __tablename__ = "microgrids"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity_kw = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    forecasts = relationship("Forecast", back_populates="microgrid")
    sensor_readings = relationship("SensorReading", back_populates="microgrid")
    alerts = relationship("Alert", back_populates="microgrid")

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


