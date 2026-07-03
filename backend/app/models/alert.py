import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    NEW = "new"
    TRIAGED = "triaged"
    ESCALATED = "escalated"
    FALSE_POSITIVE = "false_positive"
    CLOSED = "closed"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=False)          # e.g. "EDR", "Firewall", "IDS", "Simulator"
    severity = Column(Enum(Severity), nullable=False, default=Severity.MEDIUM)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.NEW)

    src_ip = Column(String, nullable=True)
    dest_ip = Column(String, nullable=True)
    asset = Column(String, nullable=True)             # affected hostname/asset
    mitre_tactic = Column(String, nullable=True)       # e.g. "Initial Access"
    mitre_technique = Column(String, nullable=True)    # e.g. "T1190"

    ioc_match = Column(String, nullable=True)          # value of matched IOC, if any
    risk_score = Column(Float, default=0.0)            # 0-100, boosted by correlation

    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    triaged_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="alerts")
