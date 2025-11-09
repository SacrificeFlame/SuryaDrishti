#!/usr/bin/env python3
"""
Initialize database and seed with default data.
This script can be run on Railway to initialize the database.
"""
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, SessionLocal
from app.models.database import Base, Microgrid, SensorReading, Device, SystemConfiguration

def init_database():
    """Initialize database tables and seed with default data"""
    print("🔧 Initializing database...")
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    db = SessionLocal()
    try:
        # Check if microgrid_001 exists
        existing_microgrid = db.query(Microgrid).filter(Microgrid.id == 'microgrid_001').first()
        
        if not existing_microgrid:
            print("📦 Seeding database with default data...")
            
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
            print("✅ Created microgrid_001")
            
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
            print("✅ Created initial sensor reading")
            
            # Create default devices
            devices = [
                Device(
                    microgrid_id='microgrid_001',
                    name="Essential Loads",
                    power_consumption_watts=5000,
                    device_type="essential",
                    is_active=True
                ),
                Device(
                    microgrid_id='microgrid_001',
                    name="Lighting System",
                    power_consumption_watts=2000,
                    device_type="essential",
                    is_active=True
                ),
                Device(
                    microgrid_id='microgrid_001',
                    name="Irrigation Pump 1",
                    power_consumption_watts=3000,
                    device_type="flexible",
                    minimum_runtime_minutes=60,
                    preferred_hours={'start': 8, 'end': 18},
                    is_active=True
                ),
                Device(
                    microgrid_id='microgrid_001',
                    name="Water Heater",
                    power_consumption_watts=2000,
                    device_type="flexible",
                    preferred_hours={'start': 10, 'end': 14},
                    is_active=True
                ),
                Device(
                    microgrid_id='microgrid_001',
                    name="Optional Loads",
                    power_consumption_watts=1000,
                    device_type="optional",
                    is_active=True
                ),
            ]
            
            for device in devices:
                existing_device = db.query(Device).filter_by(
                    microgrid_id='microgrid_001',
                    name=device.name
                ).first()
                if not existing_device:
                    db.add(device)
            
            print("✅ Created default devices")
            
            # Create default system configuration
            existing_config = db.query(SystemConfiguration).filter(
                SystemConfiguration.microgrid_id == 'microgrid_001'
            ).first()
            
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
                print("✅ Created default system configuration")
            
            db.commit()
            print("✅ Database seeded successfully!")
        else:
            print(f"✅ Microgrid {existing_microgrid.id} already exists")
        
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

