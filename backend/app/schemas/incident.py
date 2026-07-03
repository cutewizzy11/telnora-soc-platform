from datetime import datetime
from pydantic import BaseModel

from app.models.incident import IncidentStatus, IncidentSeverity


class IncidentBase(BaseModel):
    title: str
    summary: str | None = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


class IncidentCreate(IncidentBase):
    alert_ids: list[str] = []


class IncidentUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    assignee_id: str | None = None


class CommentCreate(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: str
    author_name: str | None = None
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentOut(IncidentBase):
    id: str
    status: IncidentStatus
    assignee_id: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    comments: list[CommentOut] = []

    class Config:
        from_attributes = True
