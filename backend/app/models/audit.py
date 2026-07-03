import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String, nullable=True)
    actor_email = Column(String, nullable=True)
    action = Column(String, nullable=False)       # e.g. "incident.status_change"
    target_type = Column(String, nullable=True)   # e.g. "incident"
    target_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)         # free-text / JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
