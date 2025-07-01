# medassistant/backend/app/models.py

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.db_session import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g. "admin", "operator"
    assigned_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    location = relationship("Location", back_populates="users")


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)

    users = relationship("User", back_populates="location")
    items = relationship("Item", back_populates="location")
    sensors = relationship("Sensor", back_populates="location")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    nfc_tag = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    batch = Column(String, nullable=False)
    expiry_date = Column(Date, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    status = Column(String, default="in_stock", nullable=False)

    location = relationship("Location", back_populates="items")
    events = relationship("Event", back_populates="item")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "entry", "exit", "moved"
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metadata = Column(Text, nullable=True)

    item = relationship("Item", back_populates="events")
    # Optionally, relate back to User if you wish:
    # user = relationship("User")


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)            # e.g. "Freezer 1"
    type = Column(String, nullable=False)            # "temperature", "humidity", "door", etc.
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)
    last_ping = Column(DateTime, nullable=True)

    location = relationship("Location", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)

    sensor = relationship("Sensor", back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)           # e.g. "below_threshold"
    related_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False)           # "info", "warning", "critical"
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # optional relationships:
    # item = relationship("Item")
    # sensor = relationship("Sensor")
