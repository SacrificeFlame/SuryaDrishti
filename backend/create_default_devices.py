#!/usr/bin/env python3
"""Create default devices for microgrid if none exist"""
import sys
from datetime import datetime
from app.core.database import SessionLocal
from app.models.database import Device

DEFAULT_MICROGRID_ID = 'microgrid_001'

def create_default_devices():
    db = SessionLocal()
    try:
        # Check if devices already exist
        existing = db.query(Device).filter(Device.microgrid_id == DEFAULT_MICROGRID_ID).first()
        if existing:
            print(f'✅ Devices already exist for {DEFAULT_MICROGRID_ID}')
            return
        
        # Create default devices
        devices = [
            Device(
                microgrid_id=DEFAULT_MICROGRID_ID,
                name='Essential Loads',
                power_consumption_watts=5000.0,  # 5 kW
                device_type='essential',
                minimum_runtime_minutes=0,
                priority_level=1,
                is_active=True
            ),
            Device(
                microgrid_id=DEFAULT_MICROGRID_ID,
                name='Lighting System',
                power_consumption_watts=2000.0,  # 2 kW
                device_type='essential',
                minimum_runtime_minutes=0,
                priority_level=2,
                is_active=True
            ),
            Device(
                microgrid_id=DEFAULT_MICROGRID_ID,
                name='Irrigation Pump 1',
                power_consumption_watts=3000.0,  # 3 kW
                device_type='flexible',
                minimum_runtime_minutes=30,
                preferred_hours={'start': 8, 'end': 18},
                priority_level=3,
                is_active=True
            ),
            Device(
                microgrid_id=DEFAULT_MICROGRID_ID,
                name='Water Heater',
                power_consumption_watts=2000.0,  # 2 kW
                device_type='flexible',
                minimum_runtime_minutes=15,
                preferred_hours={'start': 6, 'end': 10},
                priority_level=4,
                is_active=True
            ),
            Device(
                microgrid_id=DEFAULT_MICROGRID_ID,
                name='Optional Loads',
                power_consumption_watts=1000.0,  # 1 kW
                device_type='optional',
                minimum_runtime_minutes=0,
                priority_level=5,
                is_active=True
            ),
        ]
        
        for device in devices:
            db.add(device)
        
        db.commit()
        print(f'✅ Created {len(devices)} default devices for {DEFAULT_MICROGRID_ID}')
        for device in devices:
            print(f'  - {device.name}: {device.power_consumption_watts/1000}kW ({device.device_type})')
    except Exception as e:
        print(f'❌ Error creating devices: {e}')
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    create_default_devices()

