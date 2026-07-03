from datetime import datetime
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: str
    actor_email: str | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    details: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
