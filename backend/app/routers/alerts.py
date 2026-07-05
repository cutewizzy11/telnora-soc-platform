import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
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

CSV_COLUMNS = [
    "id",
    "title",
    "description",
    "source",
    "severity",
    "status",
    "src_ip",
    "dest_ip",
    "asset",
    "mitre_tactic",
    "mitre_technique",
    "ioc_match",
    "risk_score",
    "incident_id",
    "created_at",
    "updated_at",
    "triaged_at",
]


@router.get("", response_model=list[AlertOut])
def list_alerts(
    response: Response,
    status: AlertStatus | None = None,
    severity: Severity | None = None,
    q: str | None = Query(None, description="Search alert titles"),
    limit: int = Query(200, ge=1, le=500, description="Max number of alerts to return"),
    offset: int = Query(0, ge=0, description="Number of alerts to skip"),
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

    total = query.count()
    response.headers["X-Total-Count"] = str(total)

    return query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/export", summary="Export alerts as CSV")
def export_alerts(
    status: AlertStatus | None = None,
    severity: Severity | None = None,
    q: str | None = Query(None, description="Search alert titles"),
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

    alerts = query.order_by(Alert.created_at.desc()).all()

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for alert in alerts:
        row = {col: getattr(alert, col) for col in CSV_COLUMNS}
        if isinstance(row["severity"], Severity):
            row["severity"] = row["severity"].value
        if isinstance(row["status"], AlertStatus):
            row["status"] = row["status"].value
        writer.writerow(row)
    buffer.seek(0)

    filename = f"alerts_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
