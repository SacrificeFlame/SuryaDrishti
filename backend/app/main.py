from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import forecast, alerts, microgrid, sensors
from typing import List
import asyncio

app = FastAPI(
    title="SuryaDrishti API",
    description="Real-time solar forecasting for rural microgrids",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["forecast"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(microgrid.router, prefix="/api/v1/microgrid", tags=["microgrid"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["sensors"])

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
    return {"status": "healthy", "service": "suryादrishti"}

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


