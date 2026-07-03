from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.incident import Incident, IncidentComment, IncidentStatus
from app.models.alert import Alert
from app.models.user import User, Role
from app.schemas.incident import IncidentOut, IncidentCreate, IncidentUpdate, CommentCreate, CommentOut
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    status: IncidentStatus | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    return incident


@router.post("", response_model=IncidentOut)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD, Role.ANALYST)),
):
    incident = Incident(title=payload.title, summary=payload.summary, severity=payload.severity)
    db.add(incident)
    db.flush()

    if payload.alert_ids:
        db.query(Alert).filter(Alert.id.in_(payload.alert_ids)).update(
            {Alert.incident_id: incident.id}, synchronize_session=False
        )

    db.commit()
    db.refresh(incident)
    log_action(db, user, "incident.create", "incident", incident.id)
    return incident


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD, Role.ANALYST)),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")

    data = payload.model_dump(exclude_unset=True)
    if data.get("status") in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED) and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()
    for k, v in data.items():
        setattr(incident, k, v)

    db.commit()
    db.refresh(incident)
    log_action(db, user, "incident.update", "incident", incident.id, details=str(data))
    return incident


@router.post("/{incident_id}/comments", response_model=CommentOut)
def add_comment(
    incident_id: str,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")

    comment = IncidentComment(
        incident_id=incident_id,
        author_id=user.id,
        author_name=user.full_name,
        body=payload.body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    log_action(db, user, "incident.comment", "incident", incident.id)
    return comment
