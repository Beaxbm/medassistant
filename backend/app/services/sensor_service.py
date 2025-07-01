# medassistant/backend/app/services/sensor_service.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Sensor, SensorReading
from app.services.alert_service import check_and_send_alert  # alert stub

def ingest_and_check(
    db: Session,
    sensor_id: int,
    timestamp: datetime,
    value: float
) -> SensorReading:
    """
    Persist a sensor reading and trigger threshold alerts if needed.
    """
    # 1. Load sensor
    sensor = db.query(Sensor).get(sensor_id)
    if not sensor:
        raise ValueError("Sensor not found")

    # 2. Create and save reading
    reading = SensorReading(
        sensor_id=sensor_id,
        timestamp=timestamp,
        value=value
    )
    db.add(reading)

    # 3. Update sensor last_ping
    sensor.last_ping = datetime.utcnow()

    db.commit()
    db.refresh(reading)

    # 4. Threshold checks
    if sensor.threshold_min is not None and value < sensor.threshold_min:
        check_and_send_alert(sensor, reading, "below_threshold")
    elif sensor.threshold_max is not None and value > sensor.threshold_max:
        check_and_send_alert(sensor, reading, "above_threshold")

    return reading

