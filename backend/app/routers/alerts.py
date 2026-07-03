from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.alert import Alert, Severity, AlertStatus
from app.models.user import User, Role
from app.schemas.alert import AlertOut, AlertCreate, AlertUpdate
from app.services.correlation import correlate_alert, correlate_all_open
from app.services.audit_service import log_action
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    status: AlertStatus | None = None,
    severity: Severity | None = None,
    q: str | None = Query(None, description="Search alert titles"),
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if q:
        query = query.filter(Alert.title.ilike(f"%{q}%"))
    return query.order_by(Alert.created_at.desc()).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    return alert


@router.post("", response_model=AlertOut)
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD, Role.ANALYST)),
):
    alert = Alert(**payload.model_dump())
    correlate_alert(db, alert)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    log_action(db, user, "alert.create", "alert", alert.id)
    return alert


@router.patch("/{alert_id}", response_model=AlertOut)
def update_alert(
    alert_id: str,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD, Role.ANALYST)),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] in (AlertStatus.TRIAGED, AlertStatus.ESCALATED) and not alert.triaged_at:
        alert.triaged_at = datetime.utcnow()
    for k, v in data.items():
        setattr(alert, k, v)

    db.commit()
    db.refresh(alert)
    log_action(db, user, "alert.update", "alert", alert.id, details=str(data))
    return alert


@router.post("/correlate", summary="Re-run correlation across all NEW alerts")
def run_correlation(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD, Role.ANALYST)),
):
    updated = correlate_all_open(db)
    log_action(db, user, "alert.correlate_all", details=f"updated={updated}")
    return {"updated": updated}
