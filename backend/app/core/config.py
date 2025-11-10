from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import secrets

def generate_secret_key() -> str:
    """Generate a strong secret key for production use"""
    return secrets.token_urlsafe(32)

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SuryaDrishti"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    # CORS Configuration - Railway domains are handled dynamically in middleware
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        # Production domains
        "https://www.suryadrishti.in",
        "https://suryadrishti.in",
        # Add production domains from environment
        *[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()],
        # Railway frontend URLs (will be set in production)
        *[origin.strip() for origin in os.getenv("FRONTEND_URLS", "").split(",") if origin.strip()],
        # Common Railway patterns (will be matched dynamically)
        # Note: Railway domains like *.railway.app are handled in middleware
    ]
    
    # Database
    # Railway provides DATABASE_URL automatically for PostgreSQL
    # For local development, use SQLite
    # Note: Railway uses postgres:// but SQLAlchemy needs postgresql://
    # This will be converted in database.py
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./suryादrishti.db"
    )
    
    # PostgreSQL/TimescaleDB Configuration
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_SSL_MODE: str = os.getenv("DB_SSL_MODE", "prefer")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "False").lower() == "true"
    
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    
    # Security
    # Generate strong secret key if not provided (required in production)
    SECRET_KEY: str = os.getenv("SECRET_KEY") or (
        generate_secret_key() if os.getenv("ENVIRONMENT") == "production" else "dev-secret-key-change-in-production"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ALGORITHM: str = "HS256"
    
    # SSL/TLS Configuration
    SSL_ENABLED: bool = os.getenv("SSL_ENABLED", "False").lower() == "true"
    SSL_CERT_PATH: Optional[str] = os.getenv("SSL_CERT_PATH")
    SSL_KEY_PATH: Optional[str] = os.getenv("SSL_KEY_PATH")
    
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
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    METRICS_PATH: str = os.getenv("METRICS_PATH", "/metrics")
    
    # Backup Configuration
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "True").lower() == "true"
    BACKUP_INTERVAL_HOURS: int = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    BACKUP_STORAGE_PATH: str = os.getenv("BACKUP_STORAGE_PATH", "./backups")
    BACKUP_S3_BUCKET: Optional[str] = os.getenv("BACKUP_S3_BUCKET")
    BACKUP_S3_REGION: Optional[str] = os.getenv("BACKUP_S3_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Satellite Data API Keys
    INSAT_API_KEY: Optional[str] = os.getenv("INSAT_API_KEY")
    MOSDAC_API_KEY: Optional[str] = os.getenv("MOSDAC_API_KEY")
    NASA_API_KEY: Optional[str] = os.getenv("NASA_API_KEY")
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    SENTINEL_HUB_CLIENT_ID: Optional[str] = os.getenv("SENTINEL_HUB_CLIENT_ID")
    SENTINEL_HUB_CLIENT_SECRET: Optional[str] = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "False").lower() == "true"
    
    @property
    def database_url_processed(self) -> str:
        """Process DATABASE_URL to ensure proper format for SQLAlchemy"""
        db_url = self.DATABASE_URL
        # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        # Add SSL mode if using PostgreSQL
        if db_url.startswith("postgresql://") and "sslmode" not in db_url:
            separator = "&" if "?" in db_url else "?"
            db_url = f"{db_url}{separator}sslmode={self.DB_SSL_MODE}"
        return db_url
    
    @property
    def redis_url_processed(self) -> str:
        """Process Redis URL with authentication if needed"""
        if self.REDIS_HOST:
            auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
            ssl_part = "rediss://" if self.REDIS_SSL else "redis://"
            return f"{ssl_part}{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return self.REDIS_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()

# Validate critical settings in production
if settings.ENVIRONMENT == "production":
    if settings.SECRET_KEY == "dev-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be set in production environment!")
    if not settings.DATABASE_URL or settings.DATABASE_URL.startswith("sqlite"):
        raise ValueError("Production database must use PostgreSQL, not SQLite!")
    if not settings.ALLOWED_ORIGINS or len(settings.ALLOWED_ORIGINS) < 2:
        raise ValueError("ALLOWED_ORIGINS must include production domains!")


