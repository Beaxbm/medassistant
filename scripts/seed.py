# medassistant/scripts/seed.py

import os
from datetime import date
from sqlalchemy.orm import Session

# Adjust Python path so we can import app modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from app.db_session import engine, SessionLocal, Base
from app.models import Location, Sensor, Item, User
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    # 1. Create tables
    Base.metadata.create_all(bind=engine)

    # 2. Open session
    db: Session = SessionLocal()

    # 3. Create a sample location
    loc = Location(name="Main Warehouse", address="123 Pharma St.")
    db.add(loc)
    db.commit()
    db.refresh(loc)

    # 4. Create a sample sensor
    sensor = Sensor(
        name="Freezer 1",
        type="temperature",
        location_id=loc.id,
        threshold_min=2.0,
        threshold_max=8.0,
    )
    db.add(sensor)

    # 5. Create a sample item that expired yesterday
    item = Item(
        nfc_tag="ABC123",
        name="Vaccine X",
        batch="B001",
        expiry_date=date.today().replace(day=max(1, date.today().day - 1)),
        location_id=loc.id,
    )
    db.add(item)

    # 6. Create an admin user
    user = User(
        email="admin@example.com",
        hashed_password=pwd_ctx.hash("password"),
        role="admin",
    )
    db.add(user)

    # 7. Commit all
    db.commit()
    db.close()
    print("✅ Database seeded with sample data.")

if __name__ == "__main__":
    seed()
