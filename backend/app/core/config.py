from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SuryaDrishti"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    
    # Database
    # Railway provides DATABASE_URL automatically for PostgreSQL
    # For local development, use SQLite
    DATABASE_URL: str = "sqlite:///./suryादrishti.db"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert Railway's postgres:// to postgresql:// for SQLAlchemy compatibility
        if self.DATABASE_URL.startswith("postgres://"):
            # Use object.__setattr__ to bypass Pydantic's validation
            object.__setattr__(self, "DATABASE_URL", self.DATABASE_URL.replace("postgres://", "postgresql://", 1))
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Email Configuration
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_FROM_NAME: str = "SuryaDrishti"
    
    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    PROFILE_PICTURE_DIR: str = "uploads/profiles"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Satellite Data Sources
    INSAT_API_KEY: Optional[str] = None
    NASA_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    SENTINEL_HUB_CLIENT_ID: Optional[str] = None
    SENTINEL_HUB_CLIENT_SECRET: Optional[str] = None
    USE_MOCK_DATA: bool = False  # Default to False, can be overridden by .env
    
    # ML Models
    CLOUD_SEGMENTATION_MODEL_PATH: str = "data/models/cloud_seg_v1.pth"
    MOTION_TRACKER_MODEL_PATH: str = "data/models/motion_tracker_v1.pth"
    IRRADIANCE_MODEL_PATH: str = "data/models/irradiance_v1.pth"
    
    # Model Inference
    BATCH_SIZE: int = 8
    USE_GPU: bool = False  # Set to True if GPU available
    GPU_DEVICE: int = 0
    
    # Forecast Settings
    FORECAST_UPDATE_INTERVAL_MINUTES: int = 15
    FORECAST_HORIZONS: List[int] = [5, 10, 15, 30, 60]  # minutes
    ALERT_THRESHOLD_PERCENT: float = 20.0  # Power drop threshold
    
    # Grid Control
    ENABLE_AUTO_ACTIONS: bool = True
    BATTERY_SOC_THRESHOLD: float = 60.0  # Minimum SOC for buffer mode
    DIESEL_START_THRESHOLD_MINUTES: int = 30  # Start diesel if drop > 30 min
    
    # Data Retention
    KEEP_FORECAST_HISTORY_DAYS: int = 90
    KEEP_SENSOR_DATA_DAYS: int = 365
    
    # Monitoring
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()


