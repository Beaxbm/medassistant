# medassistant/backend/app/routes/items.py

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db_session import get_db
from app.models import Item, Event
from app.schemas import ItemResponse
from app.services.item_service import get_items
from app.auth_security import get_current_user, require_role
from app.schemas import UserResponse

router = APIRouter(
    prefix="",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

# -----------------------------------
# GET /items/ – List & search items
# -----------------------------------
@router.get("/items/", response_model=List[ItemResponse])
def list_items(
    q: Optional[str] = Query(None, description="Search term for name, batch, or tag"),
    sort: str = Query("name", description="Field to sort by"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retrieve items with optional search, sort, and pagination.
    """
    items = get_items(db, q=q, sort=sort, order=order, limit=limit, offset=offset)
    return items


# ---------------------------
# POST /scan-nfc/ – Scan tag
# ---------------------------
class NFCScan(BaseModel):
    tag_id: str
    event_type: str  # "entry" or "exit"

@router.post(
    "/scan-nfc/",
    summary="Scan an NFC tag to log entry/exit",
    dependencies=[Depends(require_role(["admin", "operator"]))],
)
def scan_nfc(
    scan: NFCScan,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log an entry or exit event for an item by its NFC tag.
    Only users with role 'admin' or 'operator' may call this.
    """
    # 1. Lookup item
    item = db.query(Item).filter(Item.nfc_tag == scan.tag_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # 2. Create event record
    event = Event(
        item_id=item.id,
        event_type=scan.event_type,
        timestamp=datetime.utcnow(),
        user_id=current_user.id,
        metadata=f"NFC {scan.event_type}"
    )
    db.add(event)
    # 3. Update item status
    if scan.event_type == "exit":
        item.status = "in_transit"
    elif scan.event_type == "entry":
        item.status = "in_stock"
    db.commit()
    return {
        "message": "Event recorded",
        "item_id": item.id,
        "item_status": item.status,
    }
