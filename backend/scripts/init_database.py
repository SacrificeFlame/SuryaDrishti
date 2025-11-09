"""
Initialize database with required tables and default microgrid.
Run this script once to set up the database.
"""
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, SessionLocal
from app.models.database import Base, Microgrid, SystemConfiguration, Device
from datetime import datetime

def init_database():
    """Create all tables and add default microgrid"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    db = SessionLocal()
    try:
        # Check if default microgrid exists
        default_mg = db.query(Microgrid).filter(Microgrid.id == "microgrid_001").first()
        if not default_mg:
            # Create default microgrid
            microgrid = Microgrid(
                id="microgrid_001",
                name="Default Microgrid",
                latitude=28.4595,
                longitude=77.0266,
                capacity_kw=50.0,
                created_at=datetime.utcnow()
            )
            db.add(microgrid)
            
            # Create default system configuration
            config = SystemConfiguration(
                microgrid_id="microgrid_001",
                battery_capacity_kwh=50.0,
                battery_max_charge_rate_kw=10.0,
                battery_max_discharge_rate_kw=10.0,
                battery_efficiency=0.95,
                battery_min_soc=0.2,
                battery_max_soc=0.95
            )
            db.add(config)
            
            # Create default essential device
            device = Device(
                microgrid_id="microgrid_001",
                name="Essential Load",
                power_consumption_watts=15000,  # 15 kW
                device_type="essential",
                is_active=True
            )
            db.add(device)
            
            db.commit()
            print("✓ Default microgrid created: microgrid_001")
            print("  Location: 28.4595°N, 77.0266°E (Delhi/NCR)")
            print("  Capacity: 50 kW")
        else:
            print("✓ Default microgrid already exists")
        
        print("\n✓ Database initialization complete!")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

