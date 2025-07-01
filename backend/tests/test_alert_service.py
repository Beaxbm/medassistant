import pytest
from datetime import datetime, timedelta

from app.models import Alert, Sensor, SensorReading, Item
from app.services.alert_service import (
    dispatch_alert,
    should_send,
    check_item_expiry,
    detect_sensor_offline,
    check_door_left_ajar
)

# Helper to create a Sensor instance
def make_sensor(id=1, last_ping=None, threshold_min=None, threshold_max=None):
    return Sensor(
        id=id,
        name=f"S{id}",
        type="temperature",
        location_id=1,
        last_ping=last_ping or datetime.utcnow() - timedelta(minutes=20),
        threshold_min=threshold_min,
        threshold_max=threshold_max
    )

# ------------------------
# Test deduplication logic
# ------------------------
def test_should_send_debounce():
    key = "unique-key"
    # First call: should send
    assert should_send(key) is True
    # Second call within TTL: should not send
    assert should_send(key) is False
    # After TTL, should send again
    # Simulate expiry by adjusting internal timestamp
    import time
    from app.services.alert_service import _last_sent, DEDUPE_TTL
    _last_sent[key] = time.time() - DEDUPE_TTL - 1
    assert should_send(key) is True

# ------------------------
# Test dispatch_alert
# ------------------------
def test_dispatch_alert_creates_alert_and_notifies(monkeypatch, tmp_path):
    # Capture notifications
    sent = []
    def fake_notify(channels, message):
        sent.append((tuple(channels), message))

    monkeypatch.setattr("app.services.alert_service._send_notifications", fake_notify)

    alert = dispatch_alert(
        category="door_left_ajar",
        message="Door has been open too long",
        related_item_id=None,
        sensor_id=2
    )
    assert isinstance(alert, Alert)
    # Verify severity and category
    assert alert.category == "door_left_ajar"
    assert alert.severity == "warning"
    # Verify notification was sent
    assert sent and sent[0][0] == ("email",)
    assert "Door has been open too long" in sent[0][1]

# ------------------------
# Test expiry check logic
# ------------------------
def test_check_item_expiry_triggers(monkeypatch):
    # Item expired yesterday
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    item = Item(id=5, nfc_tag="T5", name="Test", batch="B1",
                expiry_date=yesterday, location_id=1)
    calls = []
    monkeypatch.setattr("app.services.alert_service.dispatch_alert",
                        lambda **kwargs: calls.append(kwargs))

    # days_before=0 should catch expired items
    check_item_expiry([item], days_before=0)
    assert calls and calls[0]["category"] == "expiry_risk"

# ------------------------
# Test sensor offline detection
# ------------------------
def test_detect_sensor_offline_triggers(monkeypatch):
    # Sensor last ping > offline threshold
    old_ping = datetime.utcnow() - timedelta(minutes=30)
    sensor = make_sensor(id=7, last_ping=old_ping)
    calls = []
    monkeypatch.setattr("app.services.alert_service.dispatch_alert",
                        lambda **kwargs: calls.append(kwargs))

    detect_sensor_offline([sensor], offline_minutes=10)
    assert calls and calls[0]["category"] == "sensor_offline"

# ------------------------
# Test door left ajar logic
# ------------------------
def test_check_door_left_ajar_triggers(monkeypatch):
    # Simulate a door sensor reading older than threshold
    reading = SensorReading(
        id=1,
        sensor_id=3,
        timestamp=datetime.utcnow() - timedelta(minutes=15),
        value=1.0  # door open indicator
    )
    calls = []
    monkeypatch.setattr("app.services.alert_service.dispatch_alert",
                        lambda **kwargs: calls.append(kwargs))

    check_door_left_ajar([reading], open_value=1.0, max_open_minutes=5)
    assert calls and calls[0]["category"] == "door_left_ajar"
