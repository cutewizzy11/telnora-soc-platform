"""
Analytics & reporting endpoints: dashboard summary, MTTD/MTTR, and SLA
compliance. These compute directly from Alert/Incident timestamps rather
than needing a separate metrics store - fine at this scale, and transparent
for a portfolio project.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.config import get_settings
from app.models.alert import Alert, Severity, AlertStatus
from app.models.incident import Incident, IncidentStatus
from app.models.ioc import IndicatorOfCompromise
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
settings = get_settings()

_SLA_MINUTES = {
    Severity.CRITICAL: settings.sla_critical_minutes,
    Severity.HIGH: settings.sla_high_minutes,
    Severity.MEDIUM: settings.sla_medium_minutes,
    Severity.LOW: settings.sla_low_minutes,
    Severity.INFO: settings.sla_low_minutes,
}


@router.get("/summary")
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total_alerts = db.query(Alert).count()
    open_alerts = db.query(Alert).filter(Alert.status.in_([AlertStatus.NEW, AlertStatus.TRIAGED])).count()
    open_incidents = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS])
    ).count()
    total_iocs = db.query(IndicatorOfCompromise).count()

    by_severity = dict(
        db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    )
    by_status = dict(
        db.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all()
    )

    return {
        "total_alerts": total_alerts,
        "open_alerts": open_alerts,
        "open_incidents": open_incidents,
        "total_iocs": total_iocs,
        "alerts_by_severity": {k.value: v for k, v in by_severity.items()},
        "alerts_by_status": {k.value: v for k, v in by_status.items()},
    }


@router.get("/mttd")
def mttd(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Mean Time To Detect/Triage: created_at -> triaged_at, in minutes."""
    alerts = db.query(Alert).filter(Alert.triaged_at.isnot(None)).all()
    if not alerts:
        return {"mean_minutes": None, "sample_size": 0}
    deltas = [(a.triaged_at - a.created_at).total_seconds() / 60 for a in alerts]
    return {"mean_minutes": round(sum(deltas) / len(deltas), 1), "sample_size": len(deltas)}


@router.get("/mttr")
def mttr(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Mean Time To Resolve: incident created_at -> resolved_at, in minutes."""
    incidents = db.query(Incident).filter(Incident.resolved_at.isnot(None)).all()
    if not incidents:
        return {"mean_minutes": None, "sample_size": 0}
    deltas = [(i.resolved_at - i.created_at).total_seconds() / 60 for i in incidents]
    return {"mean_minutes": round(sum(deltas) / len(deltas), 1), "sample_size": len(deltas)}


@router.get("/sla")
def sla_compliance(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """
    % of alerts triaged within their severity's SLA window (or, for alerts
    still open, whether they're already past due).
    """
    alerts = db.query(Alert).all()
    results = {}
    for severity, sla_minutes in _SLA_MINUTES.items():
        subset = [a for a in alerts if a.severity == severity]
        if not subset:
            results[severity.value] = {"total": 0, "met_sla": 0, "pct": None, "breached_open": 0}
            continue

        met = 0
        breached_open = 0
        for a in subset:
            elapsed_ref = a.triaged_at or datetime.utcnow()
            elapsed_minutes = (elapsed_ref - a.created_at).total_seconds() / 60
            within = elapsed_minutes <= sla_minutes
            if a.triaged_at and within:
                met += 1
            elif not a.triaged_at and not within:
                breached_open += 1

        results[severity.value] = {
            "total": len(subset),
            "met_sla": met,
            "pct": round(100 * met / len(subset), 1),
            "breached_open": breached_open,
            "sla_minutes": sla_minutes,
        }
    return results
