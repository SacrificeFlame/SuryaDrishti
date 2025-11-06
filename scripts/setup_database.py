#!/usr/bin/env python3
"""
Initialize database and seed with sample data
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import engine, SessionLocal
from app.models.database import Base, Microgrid, SensorReading
from sqlalchemy import text

def setup_database():
    """Initialize database tables and seed data"""
    print("Setting up database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Microgrid).first()
        if existing:
            print("⚠️  Database already contains data. Skipping seed.")
            return
        
        # Create sample microgrids
        microgrids = [
            Microgrid(
                id="microgrid_001",
                name="Rajasthan Solar Grid 1",
                latitude=28.4595,
                longitude=77.0266,
                capacity_kw=50.0,
                created_at=datetime.utcnow()
            ),
            Microgrid(
                id="microgrid_002",
                name="Gujarat Solar Grid 2",
                latitude=23.0225,
                longitude=72.5714,
                capacity_kw=75.0,
                created_at=datetime.utcnow()
            ),
            Microgrid(
                id="microgrid_003",
                name="Tamil Nadu Solar Grid 3",
                latitude=11.1271,
                longitude=78.6569,
                capacity_kw=100.0,
                created_at=datetime.utcnow()
            )
        ]
        
        for mg in microgrids:
            db.add(mg)
        
        # Add some initial sensor readings
        for mg in microgrids:
            reading = SensorReading(
                microgrid_id=mg.id,
                irradiance=850.0,
                power_output=mg.capacity_kw * 0.8,
                temperature=32.0,
                humidity=45.0,
                wind_speed=3.5,
                wind_direction=180.0,
                timestamp=datetime.utcnow()
            )
            db.add(reading)
        
        db.commit()
        print(f"✅ Seeded {len(microgrids)} microgrids")
        print(f"✅ Seeded {len(microgrids)} sensor readings")
        
        # Display created microgrids
        print("\nCreated Microgrids:")
        for mg in microgrids:
            print(f"  - {mg.id}: {mg.name}")
            print(f"    Location: ({mg.latitude:.4f}, {mg.longitude:.4f})")
            print(f"    Capacity: {mg.capacity_kw} kW")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("\n✅ Database setup complete!")

if __name__ == "__main__":
    setup_database()


