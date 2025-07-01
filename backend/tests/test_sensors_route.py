import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, Sensor
from app.db_session import get_db

# Use an in-memory SQLite database for testing
ENGINE = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=ENGINE)

@pytest.fixture(scope="module", autouse=True)
def setup_app():
    # Create all tables in the test DB
    Base.metadata.create_all(ENGINE)

    # Override the get_db dependency to use the test session
    app.dependency_overrides[get_db] = lambda: SessionLocal()

    # Seed a sensor record for tests
    db = SessionLocal()
    db.add(Sensor(
        id=1,
        name="Test Sensor",
        type="humidity",
        threshold_min=30.0,
        threshold_max=70.0,
        location_id=1
    ))
    db.commit()
    db.close()

    yield

    # Teardown: drop all tables
    Base.metadata.drop_all(ENGINE)


client = TestClient(app)

def test_reading_success():
    payload = {
        "sensor_id": 1,
        "timestamp": "2025-06-30T14:30:00Z",
        "value": 50.0
    }
    response = client.post("/sensors/readings/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sensor_id"] == 1
    assert data["value"] == 50.0
    assert "id" in data

def test_reading_missing_sensor():
    payload = {
        "sensor_id": 999,
        "timestamp": "2025-06-30T14:30:00Z",
        "value": 50.0
    }
    response = client.post("/sensors/readings/", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Sensor not found"

