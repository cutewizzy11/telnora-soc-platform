import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class Role(str, enum.Enum):
    ADMIN = "admin"          # full platform control, user/role management
    SOC_LEAD = "soc_lead"    # manage incidents, view audit log, analytics
    ANALYST = "analyst"      # triage alerts, work incidents
    VIEWER = "viewer"        # read-only access (e.g. auditor, exec)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.ANALYST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_incidents = relationship("Incident", back_populates="assignee")
