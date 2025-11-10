"""
Prometheus metrics endpoint for monitoring
"""
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from app.core.config import settings

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    if not settings.ENABLE_METRICS:
        return {"message": "Metrics are disabled"}
    
    # Import metrics here to avoid circular imports
    from prometheus_client import Counter, Histogram, Gauge
    import time
    
    # Define metrics (these should be initialized elsewhere in production)
    # For now, return basic metrics
    metrics_data = "# SuryaDrishti Metrics\n"
    metrics_data += "# HELP http_requests_total Total HTTP requests\n"
    metrics_data += "# TYPE http_requests_total counter\n"
    metrics_data += "http_requests_total 0\n"
    
    return Response(
        content=generate_latest() if settings.ENABLE_METRICS else metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )

