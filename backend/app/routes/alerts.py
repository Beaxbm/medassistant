# medassistant/backend/app/routes/alerts.py

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db_session import get_db
from app.models import Alert
from app.schemas import AlertResponse
from app.auth_security import get_current_user, require_role

router = APIRouter(
    prefix="",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)

# --------------------------------------
# GET /alerts/ – list (active or all)
# --------------------------------------
@router.get(
    "/alerts/",
    response_model=List[AlertResponse],
    summary="List alerts",
    dependencies=[Depends(require_role(["admin", "auditor", "operator"]))]
)
def list_alerts(
    status: Optional[str] = Query(
        None,
        regex="^(active|all)$",
        description="Filter by 'active' (unresolved) or 'all'"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve alerts.  
    - If `status=active`, return only unresolved alerts.  
    - If `status=all`, return both resolved and unresolved alerts.  
    - If omitted, defaults to unresolved.
    """
    query = db.query(Alert)
    if status == "active" or status is None:
        query = query.filter(Alert.resolved == False)  # noqa: E712
    alerts = query.order_by(Alert.timestamp.desc()).all()
    return alerts


# --------------------------------------
# POST /alerts/{alert_id}/resolve
# --------------------------------------
@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Mark an alert as resolved",
    dependencies=[Depends(require_role(["admin", "auditor"]))]
)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Mark the specified alert as resolved and set its resolved_at timestamp.
    Only 'admin' or 'auditor' roles may call this.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.resolved:
        return alert

    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert

