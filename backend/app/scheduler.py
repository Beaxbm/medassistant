# medassistant/backend/app/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db_session import SessionLocal
from app.models import Sensor, SensorReading
from app.services.alert_service import (
    detect_sensor_offline,
    detect_power_failure,
    check_door_left_ajar,
    check_item_expiry,
)
from app.services.alert_service import dispatch_alert
from app.models import Item

# Configure your schedules (in minutes)
OFFLINE_CHECK_INTERVAL = 10
POWER_CHECK_INTERVAL = 5
DOOR_AJAR_CHECK_INTERVAL = 5
EXPIRY_CHECK_INTERVAL = 60  # every hour

# If you have a way to get gateway heartbeat times, replace this stub:
def _get_gateway_status() -> dict[str, datetime]:
    """
    Stub: return mapping gateway_id → last heartbeat datetime.
    In a real system, you'd query a table or external service.
    """
    # Example hardcoded gateway statuses:
    return {
        "gateway-1": datetime.utcnow() - timedelta(minutes=1),
        # Add more as needed...
    }

def _job_detect_sensor_offline():
    db: Session = SessionLocal()
    try:
        sensors = db.query(Sensor).all()
        detect_sensor_offline(sensors, offline_minutes=OFFLINE_CHECK_INTERVAL)
    finally:
        db.close()

def _job_detect_power_failure():
    gateway_status = _get_gateway_status()
    detect_power_failure(gateway_status, power_timeout_minutes=POWER_CHECK_INTERVAL)

def _job_check_door_left_ajar():
    db: Session = SessionLocal()
    try:
        # Fetch all door-type sensor readings in the last X minutes
        cutoff = datetime.utcnow() - timedelta(minutes=DOOR_AJAR_CHECK_INTERVAL)
        readings = (
            db.query(SensorReading)
            .join(Sensor, Sensor.id == SensorReading.sensor_id)
            .filter(Sensor.type == "door")
            .filter(SensorReading.timestamp <= cutoff)
            .all()
        )
        check_door_left_ajar(readings, open_value=1.0, max_open_minutes=DOOR_AJAR_CHECK_INTERVAL)
    finally:
        db.close()

def _job_check_item_expiry():
    db: Session = SessionLocal()
    try:
        items = db.query(Item).all()
        # days_before= X can be parameterized; here 0 = expired or expiring today
        check_item_expiry(items, days_before=0)
    finally:
        db.close()

def start_scheduler():
    """
    Initialize and start the background scheduler.
    Call this once on app startup.
    """
    scheduler = BackgroundScheduler(timezone="UTC")
    # Sensor offline check
    scheduler.add_job(
        _job_detect_sensor_offline,
        "interval",
        minutes=OFFLINE_CHECK_INTERVAL,
        id="sensor_offline_check",
        replace_existing=True,
    )
    # Power failure check
    scheduler.add_job(
        _job_detect_power_failure,
        "interval",
        minutes=POWER_CHECK_INTERVAL,
        id="power_failure_check",
        replace_existing=True,
    )
    # Door left ajar check
    scheduler.add_job(
        _job_check_door_left_ajar,
        "interval",
        minutes=DOOR_AJAR_CHECK_INTERVAL,
        id="door_ajar_check",
        replace_existing=True,
    )
    # Expiry risk check
    scheduler.add_job(
        _job_check_item_expiry,
        "interval",
        minutes=EXPIRY_CHECK_INTERVAL,
        id="expiry_check",
        replace_existing=True,
    )

    scheduler.start()
    print("🔔 Scheduler started with jobs: ",
          [job.id for job in scheduler.get_jobs()])
