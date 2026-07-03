from datetime import datetime
from pydantic import BaseModel

from app.models.alert import Severity, AlertStatus


class AlertBase(BaseModel):
    title: str
    description: str | None = None
    source: str
    severity: Severity = Severity.MEDIUM
    src_ip: str | None = None
    dest_ip: str | None = None
    asset: str | None = None
    mitre_tactic: str | None = None
    mitre_technique: str | None = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: AlertStatus | None = None
    severity: Severity | None = None
    incident_id: str | None = None


class AlertOut(AlertBase):
    id: str
    status: AlertStatus
    ioc_match: str | None = None
    risk_score: float
    incident_id: str | None = None
    created_at: datetime
    updated_at: datetime
    triaged_at: datetime | None = None

    class Config:
        from_attributes = True
