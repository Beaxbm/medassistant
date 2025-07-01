import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Sensor, SensorReading
from app.services.sensor_service import ingest_and_check

# Use an in-memory SQLite DB for testing
ENGINE = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=ENGINE)

@pytest.fixture(autouse=True)
def setup_db():
    # Create tables
    Base.metadata.create_all(ENGINE)
    db = SessionLocal()
    # Seed a sensor with thresholds
    sensor = Sensor(
        id=1,
        name="TempSensor1",
        type="temperature",
        threshold_min=10.0,
        threshold_max=30.0,
        location_id=1
    )
    db.add(sensor)
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(ENGINE)

def test_ingest_within_threshold(setup_db):
    db = setup_db
    reading = ingest_and_check(
        db,
        sensor_id=1,
        timestamp=datetime.utcnow(),
        value=20.0
    )
    assert isinstance(reading, SensorReading)
    assert reading.value == 20.0

def test_ingest_below_threshold_triggers_alert(monkeypatch, setup_db):
    db = setup_db
    called = {}
    def fake_alert(sensor, reading, alert_type):
        called['args'] = (sensor.id, reading.value, alert_type)
    # Monkeypatch the alert call inside sensor_service
    monkeypatch.setattr(
        "app.services.sensor_service.check_and_send_alert",
        fake_alert
    )

    reading = ingest_and_check(
        db,
        sensor_id=1,
        timestamp=datetime.utcnow(),
        value=5.0
    )
    assert called['args'] == (1, 5.0, "below_threshold")

def test_ingest_above_threshold_triggers_alert(monkeypatch, setup_db):
    db = setup_db
    called = {}
    def fake_alert(sensor, reading, alert_type):
        called['args'] = (sensor.id, reading.value, alert_type)
    monkeypatch.setattr(
        "app.services.sensor_service.check_and_send_alert",
        fake_alert
    )

    reading = ingest_and_check(
        db,
        sensor_id=1,
        timestamp=datetime.utcnow(),
        value=35.0
    )
    assert called['args'] == (1, 35.0, "above_threshold")

