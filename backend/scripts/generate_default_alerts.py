#!/usr/bin/env python3
"""
Generate default system alerts for monitoring
This ensures the system always shows some alerts to indicate it's running
"""
import sys
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.database import Alert, Microgrid

DEFAULT_MICROGRID_ID = 'microgrid_001'

def generate_default_alerts():
    """Generate default system alerts if none exist"""
    db = SessionLocal()
    try:
        # Check if microgrid exists
        microgrid = db.query(Microgrid).filter(Microgrid.id == DEFAULT_MICROGRID_ID).first()
        if not microgrid:
            print(f"❌ Microgrid {DEFAULT_MICROGRID_ID} not found. Please initialize database first.")
            return
        
        # Check if alerts already exist
        existing_alerts = db.query(Alert).filter(Alert.microgrid_id == DEFAULT_MICROGRID_ID).count()
        if existing_alerts > 0:
            print(f"✅ Alerts already exist ({existing_alerts} alerts found)")
            return
        
        # Generate default system alerts
        now = datetime.utcnow()
        default_alerts = [
            Alert(
                microgrid_id=DEFAULT_MICROGRID_ID,
                timestamp=now - timedelta(minutes=5),
                severity='info',
                message='System initialized and running normally',
                action_taken='System startup completed',
                acknowledged=0
            ),
            Alert(
                microgrid_id=DEFAULT_MICROGRID_ID,
                timestamp=now - timedelta(minutes=10),
                severity='info',
                message='Forecast generation scheduled for next 15 minutes',
                action_taken='Forecast scheduler activated',
                acknowledged=0
            ),
            Alert(
                microgrid_id=DEFAULT_MICROGRID_ID,
                timestamp=now - timedelta(hours=1),
                severity='warning',
                message='Battery SOC below 70% - monitoring charge cycle',
                action_taken='Battery charging initiated',
                acknowledged=0
            ),
            Alert(
                microgrid_id=DEFAULT_MICROGRID_ID,
                timestamp=now - timedelta(hours=2),
                severity='info',
                message='Daily performance report generated',
                action_taken='Report saved to database',
                acknowledged=1
            ),
            Alert(
                microgrid_id=DEFAULT_MICROGRID_ID,
                timestamp=now - timedelta(hours=3),
                severity='info',
                message='Solar generation peak reached - 42.5 kW',
                action_taken='Battery charging at maximum rate',
                acknowledged=0
            ),
            Alert(
                microgrid_id=DEFAULT_MICROGRID_ID,
                timestamp=now - timedelta(hours=4),
                severity='warning',
                message='Cloud coverage detected - forecast adjusted',
                action_taken='Forecast model updated with cloud data',
                acknowledged=0
            ),
        ]
        
        for alert in default_alerts:
            db.add(alert)
        
        db.commit()
        print(f"✅ Generated {len(default_alerts)} default alerts for {DEFAULT_MICROGRID_ID}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating alerts: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    generate_default_alerts()

