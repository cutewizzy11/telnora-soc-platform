"""
Lightweight correlation engine.

Matches an alert's src_ip / dest_ip against the IOC table populated by
threat_intel_service. On a match, the alert's risk_score is boosted and
ioc_match is stamped, and if the match confidence is high enough the
alert's severity is escalated - a simplified version of what a real SOC
correlation/SIEM rule engine does.
"""
from sqlalchemy.orm import Session

from app.models.alert import Alert, Severity
from app.models.ioc import IndicatorOfCompromise, IOCType

_SEVERITY_ORDER = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]


def _escalate(current: Severity, confidence: float) -> Severity:
    idx = _SEVERITY_ORDER.index(current)
    if confidence >= 90 and idx < len(_SEVERITY_ORDER) - 1:
        idx += 2
    elif confidence >= 70 and idx < len(_SEVERITY_ORDER) - 1:
        idx += 1
    return _SEVERITY_ORDER[min(idx, len(_SEVERITY_ORDER) - 1)]


def correlate_alert(db: Session, alert: Alert) -> Alert:
    candidates = [ip for ip in (alert.src_ip, alert.dest_ip) if ip]
    if not candidates:
        return alert

    match = (
        db.query(IndicatorOfCompromise)
        .filter(
            IndicatorOfCompromise.type == IOCType.IP,
            IndicatorOfCompromise.value.in_(candidates),
        )
        .order_by(IndicatorOfCompromise.confidence.desc())
        .first()
    )
    if match:
        alert.ioc_match = f"{match.source}:{match.value}"
        alert.risk_score = max(alert.risk_score or 0.0, match.confidence)
        alert.severity = _escalate(alert.severity, match.confidence)
    return alert


def correlate_all_open(db: Session) -> int:
    from app.models.alert import AlertStatus

    alerts = db.query(Alert).filter(Alert.status == AlertStatus.NEW).all()
    count = 0
    for alert in alerts:
        before = (alert.severity, alert.ioc_match)
        correlate_alert(db, alert)
        if (alert.severity, alert.ioc_match) != before:
            count += 1
    db.commit()
    return count
