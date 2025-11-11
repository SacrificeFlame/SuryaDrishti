"""
Grid Provider API endpoints
Handles grid provider information and selection for energy export.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.database import SystemConfiguration, Microgrid
from app.models.schemas import (
    GridProvider,
    GridProviderListResponse,
    GridProviderSelectionRequest,
    SystemConfigurationResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Mock grid provider data for India
# In production, this would come from a database or external API
GRID_PROVIDERS = [
    {
        "id": "bses_delhi",
        "name": "BSES Delhi",
        "description": "BSES Yamuna Power and BSES Rajdhani Power",
        "peak_rate_per_kwh": 8.5,
        "off_peak_rate_per_kwh": 4.5,
        "export_rate_per_kwh": 3.5,
        "peak_hours": {"start": 8, "end": 20},
        "coverage_areas": ["Delhi", "New Delhi", "NCR"],
        "is_available": True,
        "minimum_export_kw": 1.0,
        "maximum_export_kw": 100.0
    },
    {
        "id": "tata_power_delhi",
        "name": "Tata Power Delhi",
        "description": "Tata Power Delhi Distribution Limited",
        "peak_rate_per_kwh": 9.0,
        "off_peak_rate_per_kwh": 4.8,
        "export_rate_per_kwh": 4.0,
        "peak_hours": {"start": 9, "end": 21},
        "coverage_areas": ["Delhi", "New Delhi"],
        "is_available": True,
        "minimum_export_kw": 1.0,
        "maximum_export_kw": 50.0
    },
    {
        "id": "reliance_mumbai",
        "name": "Reliance Energy Mumbai",
        "description": "Reliance Infrastructure Limited - Mumbai",
        "peak_rate_per_kwh": 10.0,
        "off_peak_rate_per_kwh": 5.5,
        "export_rate_per_kwh": 4.5,
        "peak_hours": {"start": 8, "end": 22},
        "coverage_areas": ["Mumbai", "Maharashtra"],
        "is_available": True,
        "minimum_export_kw": 2.0,
        "maximum_export_kw": 200.0
    },
    {
        "id": "adani_mumbai",
        "name": "Adani Electricity Mumbai",
        "description": "Adani Electricity Mumbai Limited",
        "peak_rate_per_kwh": 9.5,
        "off_peak_rate_per_kwh": 5.0,
        "export_rate_per_kwh": 4.2,
        "peak_hours": {"start": 8, "end": 20},
        "coverage_areas": ["Mumbai", "Maharashtra"],
        "is_available": True,
        "minimum_export_kw": 1.0,
        "maximum_export_kw": 150.0
    },
    {
        "id": "torrent_gujarat",
        "name": "Torrent Power Gujarat",
        "description": "Torrent Power Limited - Gujarat",
        "peak_rate_per_kwh": 8.0,
        "off_peak_rate_per_kwh": 4.2,
        "export_rate_per_kwh": 3.8,
        "peak_hours": {"start": 7, "end": 19},
        "coverage_areas": ["Gujarat", "Ahmedabad", "Surat"],
        "is_available": True,
        "minimum_export_kw": 1.0,
        "maximum_export_kw": 100.0
    },
    {
        "id": "cseb_rajasthan",
        "name": "Rajasthan State Electricity Board",
        "description": "Rajasthan Vidyut Prasaran Nigam Limited",
        "peak_rate_per_kwh": 7.5,
        "off_peak_rate_per_kwh": 4.0,
        "export_rate_per_kwh": 3.2,
        "peak_hours": {"start": 8, "end": 20},
        "coverage_areas": ["Rajasthan", "Jaipur", "Jodhpur"],
        "is_available": True,
        "minimum_export_kw": 1.0,
        "maximum_export_kw": 75.0
    }
]


def get_available_providers_for_location(lat: float, lon: float) -> List[GridProvider]:
    """
    Get available grid providers for a given location.
    In production, this would use geolocation data to determine available providers.
    For now, we return all providers that are available.
    """
    # Simple location-based filtering (can be enhanced with actual geolocation data)
    # For demo purposes, we'll return all available providers
    providers = []
    
    for provider_data in GRID_PROVIDERS:
        if provider_data["is_available"]:
            providers.append(GridProvider(**provider_data))
    
    return providers


@router.get("/grid-providers", response_model=GridProviderListResponse)
async def get_grid_providers(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    microgrid_id: str = Query(..., description="Microgrid ID"),
    db: Session = Depends(get_db)
):
    """
    Get available grid providers for a given location.
    Returns list of providers with pricing information.
    """
    try:
        # Verify microgrid exists
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        # Get available providers for location
        providers = get_available_providers_for_location(lat, lon)
        
        # Get current configuration to see if a provider is already selected
        config = db.query(SystemConfiguration).filter(
            SystemConfiguration.microgrid_id == microgrid_id
        ).first()
        
        selected_provider_id = None
        if config:
            # Check if there's a selected provider (we'll use grid_export_rate_per_kwh to match)
            # In a real system, we'd store provider_id in the config
            # For now, we'll check if export is enabled and try to match by rate
            if config.grid_export_enabled:
                # Try to find matching provider by export rate (within 0.5 ₹/kWh tolerance)
                for provider in providers:
                    if abs(provider.export_rate_per_kwh - config.grid_export_rate_per_kwh) < 0.5:
                        selected_provider_id = provider.id
                        break
        
        return GridProviderListResponse(
            location={"lat": lat, "lon": lon},
            providers=providers,
            selected_provider_id=selected_provider_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting grid providers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get grid providers: {str(e)}")


@router.post("/grid-providers/select", response_model=SystemConfigurationResponse)
async def select_grid_provider(
    microgrid_id: str,
    selection: GridProviderSelectionRequest,
    db: Session = Depends(get_db)
):
    """
    Select a grid provider and update system configuration.
    """
    try:
        # Verify microgrid exists
        microgrid = db.query(Microgrid).filter(Microgrid.id == microgrid_id).first()
        if not microgrid:
            raise HTTPException(status_code=404, detail=f"Microgrid {microgrid_id} not found")
        
        # Find the selected provider
        provider = None
        for provider_data in GRID_PROVIDERS:
            if provider_data["id"] == selection.provider_id:
                provider = GridProvider(**provider_data)
                break
        
        if not provider:
            raise HTTPException(status_code=404, detail=f"Grid provider {selection.provider_id} not found")
        
        if not provider.is_available:
            raise HTTPException(status_code=400, detail=f"Grid provider {selection.provider_id} is not available")
        
        # Get or create system configuration
        config = db.query(SystemConfiguration).filter(
            SystemConfiguration.microgrid_id == microgrid_id
        ).first()
        
        if not config:
            # Create new configuration with provider settings
            config = SystemConfiguration(
                microgrid_id=microgrid_id,
                battery_capacity_kwh=50.0,
                battery_max_charge_rate_kw=10.0,
                battery_max_discharge_rate_kw=10.0,
                battery_efficiency=0.95,
                battery_min_soc=0.2,
                battery_max_soc=0.95,
                grid_peak_rate_per_kwh=provider.peak_rate_per_kwh,
                grid_off_peak_rate_per_kwh=provider.off_peak_rate_per_kwh,
                grid_peak_hours=provider.peak_hours,
                grid_export_rate_per_kwh=provider.export_rate_per_kwh,
                grid_export_enabled=selection.enable_export,
                generator_fuel_consumption_l_per_kwh=0.25,
                generator_fuel_cost_per_liter=80.0,
                generator_min_runtime_minutes=30,
                generator_max_power_kw=20.0,
                optimization_mode='cost',
                safety_margin_critical_loads=0.1
            )
            db.add(config)
        else:
            # Update existing configuration with provider settings
            config.grid_peak_rate_per_kwh = provider.peak_rate_per_kwh
            config.grid_off_peak_rate_per_kwh = provider.off_peak_rate_per_kwh
            config.grid_peak_hours = provider.peak_hours
            config.grid_export_rate_per_kwh = provider.export_rate_per_kwh
            config.grid_export_enabled = selection.enable_export
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"Selected grid provider {selection.provider_id} for microgrid {microgrid_id}")
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error selecting grid provider: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to select grid provider: {str(e)}")

