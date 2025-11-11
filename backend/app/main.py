from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1 import forecast, alerts, microgrid, sensors, satellite, auth
from app.api.v1 import forecast_microgrid, debug, devices, schedules, configurations, forecast_validation, forecast_run, notifications, reports, db_init, metrics, grid_providers
from app.models.database import Base
from app.core.database import engine
from typing import List
import asyncio
import logging

logger = logging.getLogger(__name__)

# Helper function to check if origin is allowed (defined before middleware)
def is_origin_allowed(origin: str) -> bool:
    """Check if origin is allowed for CORS"""
    if not origin:
        return False
    
    # Check if origin is in allowed list
    if origin in settings.ALLOWED_ORIGINS:
        return True
    
    # Check if origin is a Railway domain
    if origin.endswith(".railway.app") or origin.endswith(".up.railway.app"):
        return True
    
    # Check if origin is localhost (development)
    if settings.DEBUG and ("localhost" in origin or "127.0.0.1" in origin):
        return True
    
    # Check if origin matches custom domain pattern (suryadrishti.in)
    if "suryadrishti.in" in origin:
        return True
    
    # Check if any allowed origin domain is in the request origin
    for allowed_origin in settings.ALLOWED_ORIGINS:
        if allowed_origin and "." in allowed_origin:
            # Extract domain from allowed origin (remove protocol)
            domain = allowed_origin.replace("https://", "").replace("http://", "").split("/")[0]
            if domain in origin:
                return True
    
    return False

app = FastAPI(
    title="SuryaDrishti API",
    description="Real-time solar forecasting for rural microgrids",
    version="1.0.0"
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup and seed default data"""
    try:
        # Create all tables (this will create new tables but won't modify existing ones)
        # For production, you should use Alembic migrations to add new columns
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
        
        # Try to add generator_status column if it doesn't exist (for existing databases)
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(engine)
            if inspector.has_table('system_configurations'):
                columns = [col['name'] for col in inspector.get_columns('system_configurations')]
                if 'generator_status' not in columns:
                    logger.info("Adding generator_status column to system_configurations table")
                    with engine.connect() as conn:
                        # Use ALTER TABLE to add column (PostgreSQL syntax)
                        db_url = settings.database_url_processed
                        if db_url and 'postgresql' in db_url:
                            conn.execute(text("ALTER TABLE system_configurations ADD COLUMN IF NOT EXISTS generator_status VARCHAR DEFAULT 'off'"))
                            conn.commit()
                        elif db_url and 'sqlite' in db_url:
                            # SQLite syntax (no IF NOT EXISTS in older versions)
                            try:
                                conn.execute(text("ALTER TABLE system_configurations ADD COLUMN generator_status VARCHAR DEFAULT 'off'"))
                                conn.commit()
                            except Exception as sqlite_error:
                                if 'duplicate column' in str(sqlite_error).lower() or 'already exists' in str(sqlite_error).lower():
                                    logger.info("Column generator_status already exists")
                                else:
                                    raise
                    logger.info("Successfully added generator_status column")
        except Exception as migrate_error:
            logger.warning(f"Could not add generator_status column (may already exist): {migrate_error}")
            # Continue - column might already exist
        
        # Try to add solar_provider and battery_type columns to users table if they don't exist
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(engine)
            if inspector.has_table('users'):
                columns = [col['name'] for col in inspector.get_columns('users')]
                with engine.connect() as conn:
                    db_url = settings.database_url_processed
                    if 'solar_provider' not in columns:
                        logger.info("Adding solar_provider column to users table")
                        if db_url and 'postgresql' in db_url:
                            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS solar_provider VARCHAR"))
                            conn.commit()
                        elif db_url and 'sqlite' in db_url:
                            try:
                                conn.execute(text("ALTER TABLE users ADD COLUMN solar_provider VARCHAR"))
                                conn.commit()
                            except Exception as sqlite_error:
                                if 'duplicate column' in str(sqlite_error).lower() or 'already exists' in str(sqlite_error).lower():
                                    logger.info("Column solar_provider already exists")
                                else:
                                    raise
                        logger.info("Successfully added solar_provider column")
                    
                    if 'battery_type' not in columns:
                        logger.info("Adding battery_type column to users table")
                        if db_url and 'postgresql' in db_url:
                            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS battery_type VARCHAR"))
                            conn.commit()
                        elif db_url and 'sqlite' in db_url:
                            try:
                                conn.execute(text("ALTER TABLE users ADD COLUMN battery_type VARCHAR"))
                                conn.commit()
                            except Exception as sqlite_error:
                                if 'duplicate column' in str(sqlite_error).lower() or 'already exists' in str(sqlite_error).lower():
                                    logger.info("Column battery_type already exists")
                                else:
                                    raise
                        logger.info("Successfully added battery_type column")
        except Exception as migrate_error:
            logger.warning(f"Could not add user device columns (may already exist): {migrate_error}")
            # Continue - columns might already exist
        
        # Seed default data if microgrid_001 doesn't exist
        from app.core.database import SessionLocal
        from app.models.database import Microgrid, SensorReading, Device, SystemConfiguration
        from datetime import datetime
        
        db = SessionLocal()
        try:
            existing_microgrid = db.query(Microgrid).filter(Microgrid.id == 'microgrid_001').first()
            
            if not existing_microgrid:
                logger.info("Seeding database with default data...")
                
                # Create microgrid
                microgrid = Microgrid(
                    id='microgrid_001',
                    name='Rajasthan Solar Grid 1',
                    latitude=28.4595,
                    longitude=77.0266,
                    capacity_kw=50.0,
                    created_at=datetime.utcnow()
                )
                db.add(microgrid)
                
                # Create sensor reading
                sensor_reading = SensorReading(
                    microgrid_id='microgrid_001',
                    irradiance=850.0,  # Good irradiance during day
                    power_output=42.5,  # Solar panels generating power (85% of 50kW capacity)
                    temperature=32.0,
                    humidity=45.0,
                    wind_speed=3.5,
                    wind_direction=180.0,
                    timestamp=datetime.utcnow()
                )
                db.add(sensor_reading)
                
                # Create default devices
                devices = [
                    Device(microgrid_id='microgrid_001', name="Essential Loads", power_consumption_watts=5000, device_type="essential", is_active=True),
                    Device(microgrid_id='microgrid_001', name="Lighting System", power_consumption_watts=2000, device_type="essential", is_active=True),
                    Device(microgrid_id='microgrid_001', name="Irrigation Pump 1", power_consumption_watts=3000, device_type="flexible", minimum_runtime_minutes=60, preferred_hours={'start': 8, 'end': 18}, is_active=True),
                    Device(microgrid_id='microgrid_001', name="Water Heater", power_consumption_watts=2000, device_type="flexible", preferred_hours={'start': 10, 'end': 14}, is_active=True),
                    Device(microgrid_id='microgrid_001', name="Optional Loads", power_consumption_watts=1000, device_type="optional", is_active=True),
                ]
                
                for device in devices:
                    existing_device = db.query(Device).filter_by(microgrid_id='microgrid_001', name=device.name).first()
                    if not existing_device:
                        db.add(device)
                
                # Create default system configuration
                existing_config = db.query(SystemConfiguration).filter(SystemConfiguration.microgrid_id == 'microgrid_001').first()
                if not existing_config:
                    config = SystemConfiguration(
                        microgrid_id='microgrid_001',
                        battery_capacity_kwh=100.0,
                        battery_max_charge_rate_kw=20.0,
                        battery_max_discharge_rate_kw=20.0,
                        battery_min_soc=0.2,
                        battery_max_soc=0.95,
                        battery_efficiency=0.95,
                        grid_peak_rate_per_kwh=10.0,
                        grid_off_peak_rate_per_kwh=5.0,
                        grid_peak_hours={'start': 8, 'end': 20},
                        grid_export_rate_per_kwh=4.0,
                        grid_export_enabled=True,
                        generator_fuel_cost_per_liter=85.0,
                        generator_fuel_consumption_l_per_kwh=0.25,
                        generator_min_runtime_minutes=30,
                        generator_max_power_kw=20.0,
                        generator_status='off',
                        optimization_mode='cost',
                        safety_margin_critical_loads=0.1
                    )
                    db.add(config)
                
                db.commit()
                logger.info("✅ Database seeded with default data")
            else:
                logger.info(f"Database already has microgrid {existing_microgrid.id}")
            
            # Generate default alerts if none exist
            from app.models.database import Alert
            from datetime import timedelta
            existing_alerts = db.query(Alert).filter(Alert.microgrid_id == 'microgrid_001').count()
            if existing_alerts == 0:
                logger.info("Generating default system alerts...")
                now = datetime.utcnow()
                default_alerts = [
                    Alert(
                        microgrid_id='microgrid_001',
                        timestamp=now - timedelta(minutes=5),
                        severity='info',
                        message='System initialized and running normally',
                        action_taken='System startup completed',
                        acknowledged=0
                    ),
                    Alert(
                        microgrid_id='microgrid_001',
                        timestamp=now - timedelta(minutes=10),
                        severity='info',
                        message='Forecast generation scheduled for next 15 minutes',
                        action_taken='Forecast scheduler activated',
                        acknowledged=0
                    ),
                    Alert(
                        microgrid_id='microgrid_001',
                        timestamp=now - timedelta(hours=1),
                        severity='warning',
                        message='Battery SOC below 70% - monitoring charge cycle',
                        action_taken='Battery charging initiated',
                        acknowledged=0
                    ),
                    Alert(
                        microgrid_id='microgrid_001',
                        timestamp=now - timedelta(hours=2),
                        severity='info',
                        message='Daily performance report generated',
                        action_taken='Report saved to database',
                        acknowledged=1
                    ),
                ]
                for alert in default_alerts:
                    db.add(alert)
                db.commit()
                logger.info(f"✅ Generated {len(default_alerts)} default alerts")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to seed database: {e}", exc_info=True)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

# CORS Middleware - Allow Railway domains dynamically
# Use a more permissive approach for Railway deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - Railway domains will be validated in custom middleware
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Handle OPTIONS preflight requests explicitly for CORS
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle OPTIONS preflight requests for CORS - allows Railway and custom domains"""
    origin = request.headers.get("origin")
    response = JSONResponse(content={}, status_code=200)
    
    if origin and is_origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    elif settings.DEBUG:
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# Global exception handler to ensure CORS headers on all errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    origin = request.headers.get("origin")
    
    headers = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
    }
    
    if origin and is_origin_allowed(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    elif settings.DEBUG:
        headers["Access-Control-Allow-Origin"] = "*"
    
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers=headers
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    origin = request.headers.get("origin")
    headers = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
    }
    
    if origin and is_origin_allowed(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    elif settings.DEBUG:
        headers["Access-Control-Allow-Origin"] = "*"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    origin = request.headers.get("origin")
    headers = {
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
    }
    
    if origin and is_origin_allowed(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    elif settings.DEBUG:
        headers["Access-Control-Allow-Origin"] = "*"
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers=headers
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["forecast"])
app.include_router(forecast_microgrid.router, prefix="/api/v1/forecast", tags=["forecast"])
app.include_router(forecast_run.router, tags=["forecast"])  # /api/run endpoint (no prefix)
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(microgrid.router, prefix="/api/v1/microgrid", tags=["microgrid"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["sensors"])
app.include_router(satellite.router, prefix="/api/v1/satellite", tags=["satellite"])
app.include_router(devices.router, prefix="/api/v1", tags=["devices"])
app.include_router(schedules.router, prefix="/api/v1", tags=["schedules"])
app.include_router(configurations.router, prefix="/api/v1", tags=["configurations"])
app.include_router(grid_providers.router, prefix="/api/v1", tags=["grid-providers"])
app.include_router(forecast_validation.router, prefix="/api/v1", tags=["forecast-validation"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(db_init.router, prefix="/api/v1", tags=["database"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "suryादrishti"}

@app.get("/api/v1/health/database")
async def health_check_database():
    """Health check endpoint that verifies database connectivity and microgrid existence"""
    try:
        from app.core.database import SessionLocal
        from app.models.database import Microgrid
        
        db = SessionLocal()
        try:
            # Test database connection
            microgrid_count = db.query(Microgrid).count()
            microgrid_001 = db.query(Microgrid).filter(Microgrid.id == 'microgrid_001').first()
            
            return {
                "status": "healthy",
                "database": "connected",
                "microgrid_count": microgrid_count,
                "microgrid_001_exists": microgrid_001 is not None,
                "microgrid_001_details": {
                    "id": microgrid_001.id,
                    "name": microgrid_001.name,
                    "latitude": microgrid_001.latitude,
                    "longitude": microgrid_001.longitude,
                    "capacity_kw": microgrid_001.capacity_kw
                } if microgrid_001 else None
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any messages from client
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Function to send updates from anywhere in the app
async def send_alert(alert: dict):
    await manager.broadcast({
        "type": "alert",
        "payload": alert
    })

async def send_system_status(status: dict):
    await manager.broadcast({
        "type": "system_status",
        "payload": status
    })

async def send_forecast_update(forecast: dict):
    await manager.broadcast({
        "type": "new_forecast",
        "payload": forecast
    })


