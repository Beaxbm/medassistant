# medassistant/backend/app/services/item_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.models import Item


def get_items(
    db: Session,
    q: Optional[str] = None,
    sort: str = "name",
    order: str = "asc",
    limit: int = 100,
    offset: int = 0
) -> List[Item]:
    """
    Retrieve items with optional search, sorting, and pagination.

    - q: search term against name, batch, or nfc_tag
    - sort: column name to sort by (must be an Item attribute)
    - order: 'asc' or 'desc'
    - limit: maximum number of records to return
    - offset: number of records to skip
    """
    query = db.query(Item)

    # Search filter
    if q:
        like_term = f"%{q}%"
        query = query.filter(
            or_(
                Item.name.ilike(like_term),
                Item.batch.ilike(like_term),
                Item.nfc_tag.ilike(like_term),
            )
        )

    # Sorting
    sort_col = getattr(Item, sort, None)
    if not sort_col:
        sort_col = Item.name  # default fallback
    if order.lower() == "desc":
        query = query.order_by(desc(sort_col))
    else:
        query = query.order_by(asc(sort_col))

    # Pagination
    query = query.offset(offset).limit(limit)

    return query.all()

