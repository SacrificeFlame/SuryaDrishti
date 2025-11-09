from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1 import forecast, alerts, microgrid, sensors, satellite, auth
from app.api.v1 import forecast_microgrid, debug, devices, schedules, configurations, forecast_validation, forecast_run, notifications, reports
from app.models.database import Base
from app.core.database import engine
from typing import List
import asyncio
import logging

logger = logging.getLogger(__name__)

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
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
        
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
                    irradiance=850.0,
                    power_output=40.0,
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
                        grid_price_per_kwh=8.5,
                        generator_fuel_cost_per_liter=85.0,
                        generator_fuel_consumption_per_kw=0.3,
                        optimization_preferences={'minimize_grid_import': True, 'maximize_solar_usage': True},
                        safety_margin=0.1
                    )
                    db.add(config)
                
                db.commit()
                logger.info("✅ Database seeded with default data")
            else:
                logger.info(f"Database already has microgrid {existing_microgrid.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to seed database: {e}", exc_info=True)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

# CORS Middleware - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add CORS headers to all responses via middleware (runs after CORS middleware)
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    # Ensure CORS headers are always present
    if "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = "*"
    if "Access-Control-Allow-Methods" not in response.headers:
        response.headers["Access-Control-Allow-Methods"] = "*"
    if "Access-Control-Allow-Headers" not in response.headers:
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Global exception handler to ensure CORS headers on all errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"}
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
app.include_router(forecast_validation.router, prefix="/api/v1", tags=["forecast-validation"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(db_init.router, prefix="/api/v1", tags=["database"])

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


