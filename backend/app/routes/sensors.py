# medassistant/backend/app/routes/sensors.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db_session import get_db
from app.schemas import SensorReadingCreate, SensorReadingResponse
from app.services.sensor_service import ingest_and_check

router = APIRouter(
    prefix="",
    tags=["sensors"],
    responses={404: {"description": "Not found"}},
)

@router.post("/sensors/readings/", response_model=SensorReadingResponse)
def ingest_reading(
    reading_in: SensorReadingCreate,
    db: Session = Depends(get_db),
):
    """
    Ingest a new sensor reading, persist it, update the sensor's last_ping,
    and trigger threshold-based alerts if the reading is out of range.

    - **sensor_id**: ID of the sensor sending the reading
    - **timestamp**: UTC timestamp of the reading
    - **value**: Measured value (e.g., temperature, humidity)
    """
    try:
        reading = ingest_and_check(
            db=db,
            sensor_id=reading_in.sensor_id,
            timestamp=reading_in.timestamp,
            value=reading_in.value,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return reading
