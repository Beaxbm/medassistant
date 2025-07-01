# medassistant/backend/app/routes/sensors_status.py

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db_session import get_db
from app.models import Sensor, SensorReading
from app.schemas import SensorStatusItem

router = APIRouter(
    prefix="",
    tags=["sensors-status"],
    responses={404: {"description": "Not found"}},
)

# How long without a ping marks a sensor offline (in seconds)
OFFLINE_THRESHOLD = 10 * 60  # 10 minutes

@router.get("/sensors/status/", response_model=List[SensorStatusItem])
def get_sensors_status(db: Session = Depends(get_db)):
    """
    Return the latest status for each sensor, including:
    - current value (if any)
    - thresholds
    - last ping timestamp
    - overall status: "ok", "warning", "danger", or "offline"
    """
    sensors = db.query(Sensor).all()
    now = datetime.utcnow()
    statuses: List[SensorStatusItem] = []

    for sensor in sensors:
        # Fetch latest reading if available
        reading: Optional[SensorReading] = (
            db.query(SensorReading)
              .filter(SensorReading.sensor_id == sensor.id)
              .order_by(SensorReading.timestamp.desc())
              .first()
        )
        value = reading.value if reading else None

        # Determine status
        status: str
        # Check offline first
        if not sensor.last_ping or (now - sensor.last_ping).total_seconds() > OFFLINE_THRESHOLD:
            status = "offline"
        # Check thresholds
        elif sensor.threshold_min is not None and value is not None and value < sensor.threshold_min:
            status = "danger"
        elif sensor.threshold_max is not None and value is not None and value > sensor.threshold_max:
            status = "danger"
        # If within 10% of threshold, mark warning (optional)
        elif sensor.threshold_min is not None and value is not None and value < (sensor.threshold_min + (sensor.threshold_max - sensor.threshold_min) * 0.1):
            status = "warning"
        elif sensor.threshold_max is not None and value is not None and value > (sensor.threshold_max - (sensor.threshold_max - sensor.threshold_min) * 0.1):
            status = "warning"
        else:
            status = "ok"

        statuses.append(
            SensorStatusItem(
                sensor_id=sensor.id,
                name=sensor.name,
                type=sensor.type,
                last_ping=sensor.last_ping,
                value=value,
                threshold_min=sensor.threshold_min,
                threshold_max=sensor.threshold_max,
                status=status,
            )
        )

    return statuses
