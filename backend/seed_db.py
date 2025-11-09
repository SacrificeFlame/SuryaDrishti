#!/usr/bin/env python3
"""Quick script to seed database with microgrid data"""
import sys
from datetime import datetime
from app.core.database import engine, SessionLocal
from app.models.database import Base, Microgrid, SensorReading

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    existing = db.query(Microgrid).filter(Microgrid.id == 'microgrid_001').first()
    if not existing:
        mg = Microgrid(
            id='microgrid_001',
            name='Rajasthan Solar Grid 1',
            latitude=28.4595,
            longitude=77.0266,
            capacity_kw=50.0,
            created_at=datetime.utcnow()
        )
        db.add(mg)
        
        sr = SensorReading(
            microgrid_id='microgrid_001',
            irradiance=850.0,
            power_output=40.0,
            temperature=32.0,
            humidity=45.0,
            wind_speed=3.5,
            wind_direction=180.0,
            timestamp=datetime.utcnow()
        )
        db.add(sr)
        db.commit()
        print('✅ Created microgrid_001 and sensor reading')
    else:
        print(f'✅ Microgrid {existing.id} already exists')
finally:
    db.close()

