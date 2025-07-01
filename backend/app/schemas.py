from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# ------------------------
# Auth schemas
# ------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


# ------------------------
# Location
# ------------------------
class LocationResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None

    class Config:
        orm_mode = True


# ------------------------
# Item & Event schemas
# ------------------------
class EventCreate(BaseModel):
    item_id: int
    event_type: str  # "entry", "exit", "moved"
    user_id: int
    metadata: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    item_id: int
    event_type: str
    timestamp: datetime
    user_id: int
    metadata: Optional[str] = None

    class Config:
        orm_mode = True


class ItemCreate(BaseModel):
    nfc_tag: str
    name: str
    batch: str
    expiry_date: date
    location_id: int


class ItemResponse(BaseModel):
    id: int
    nfc_tag: str
    name: str
    batch: str
    expiry_date: date
    status: str
    location: LocationResponse
    events: Optional[List[EventResponse]] = []

    class Config:
        orm_mode = True


# ------------------------
# Sensor & Reading schemas
# ------------------------
class SensorReadingCreate(BaseModel):
    sensor_id: int
    timestamp: datetime
    value: float


class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: int
    timestamp: datetime
    value: float

    class Config:
        orm_mode = True


class SensorStatusItem(BaseModel):
    sensor_id: int
    name: str
    type: str
    last_ping: Optional[datetime]
    value: Optional[float]
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    status: str  # "ok", "warning", "danger", "offline"

    class Config:
        orm_mode = True


# ------------------------
# Alert schemas
# ------------------------
class AlertResponse(BaseModel):
    id: int
    category: str
    related_item_id: Optional[int]
    sensor_id: Optional[int]
    timestamp: datetime
    message: str
    severity: str
    resolved: bool
    resolved_at: Optional[datetime]

    class Config:
        orm_mode = True
