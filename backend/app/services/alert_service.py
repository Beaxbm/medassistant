# medassistant/backend/app/services/alert_service.py
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Alert, Sensor, SensorReading, Item, Event
from app.db_session import SessionLocal

# In-memory dedupe cache: key → timestamp of last sent
_last_sent: dict[str, float] = {}

# Configuration of alert types → severity & channels
ALERT_CONFIG: dict[str, dict] = {
    "below_threshold":   {"severity": "warning",  "channels": ["email"]},
    "above_threshold":   {"severity": "warning",  "channels": ["email"]},
    "expiry_risk":       {"severity": "critical", "channels": ["email","sms","webhook"]},
    "unauthorized_move": {"severity": "critical", "channels": ["email","sms","webhook"]},
    "sensor_offline":    {"severity": "info",     "channels": []},     # dashboard only
    "power_failure":     {"severity": "critical", "channels": ["email","sms","webhook"]},
    "door_left_ajar":    {"severity": "warning",  "channels": ["email"]},
}

DEDUPE_TTL = 3600  # seconds: don’t re-send same alert key within this window

def should_send(key: str, ttl: int = DEDUPE_TTL) -> bool:
    now = time.time()
    last = _last_sent.get(key, 0)
    if now - last > ttl:
        _last_sent[key] = now
        return True
    return False

def _send_notifications(channels: list[str], message: str):
    """
    Stub: integrate with real email/SMS/Webhook services here.
    """
    # e.g., send via SendGrid, Twilio, HTTP POST to webhook URL…
    for ch in channels:
        print(f"[notify:{ch}] {message}")

def dispatch_alert(
    category: str,
    message: str,
    related_item_id: int | None = None,
    sensor_id: int | None = None
) -> Alert:
    """
    Create an Alert record (if not deduped) and send notifications.
    """
    cfg = ALERT_CONFIG.get(category)
    if not cfg:
        raise ValueError(f"Unknown alert category '{category}'")

    key = f"{category}:{related_item_id or ''}:{sensor_id or ''}"
    if not should_send(key):
        # skip duplicate
        return None  # or retrieve existing alert if needed

    # Persist alert
    db: Session = SessionLocal()
    alert = Alert(
        category=category,
        related_item_id=related_item_id,
        sensor_id=sensor_id,
        timestamp=datetime.utcnow(),
        message=message,
        severity=cfg["severity"],
        resolved=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Send notifications
    _send_notifications(cfg["channels"], message)
    db.close()
    return alert

# ----- Rule implementations -----

def check_item_expiry(
    items: list[Item],
    days_before: int = 0
):
    """
    For each item, if expiry_date <= today + days_before, raise expiry_risk.
    """
    today = datetime.utcnow().date()
    threshold = today + timedelta(days=days_before)
    for item in items:
        if item.expiry_date <= threshold:
            msg = (
                f"Item #{item.id} ('{item.name}') expired on {item.expiry_date}"
                if item.expiry_date < today
                else f"Item #{item.id} ('{item.name}') will expire on {item.expiry_date}"
            )
            dispatch_alert("expiry_risk", msg, related_item_id=item.id)

def detect_sensor_offline(
    sensors: list[Sensor],
    offline_minutes: int = 10
):
    """
    If a sensor’s last_ping is older than X minutes, alert.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=offline_minutes)
    for sensor in sensors:
        if not sensor.last_ping or sensor.last_ping < cutoff:
            msg = f"Sensor '{sensor.name}' (ID {sensor.id}) offline since {sensor.last_ping}"
            dispatch_alert("sensor_offline", msg, sensor_id=sensor.id)

def detect_power_failure(
    gateway_status: dict[str, datetime],
    power_timeout_minutes: int = 5
):
    """
    gateway_status: mapping gateway_id → last_heartbeat datetime
    """
    cutoff = datetime.utcnow() - timedelta(minutes=power_timeout_minutes)
    for gw_id, last in gateway_status.items():
        if last < cutoff:
            msg = f"Gateway '{gw_id}' lost power since {last}"
            dispatch_alert("power_failure", msg)

def check_door_left_ajar(
    readings: list[SensorReading],
    open_value: float = 1.0,
    max_open_minutes: int = 5
):
    """
    For door sensors, if a reading indicates 'open' and has
    not changed for more than max_open_minutes, alert.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=max_open_minutes)
    for r in readings:
        if r.value == open_value and r.timestamp < cutoff:
            msg = f"Door sensor {r.sensor_id} has been open since {r.timestamp}"
            dispatch_alert("door_left_ajar", msg, sensor_id=r.sensor_id)
