import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, Text, Float

from app.database import Base


class IOCType(str, enum.Enum):
    IP = "ip"
    DOMAIN = "domain"
    HASH = "hash"
    CVE = "cve"


class IndicatorOfCompromise(Base):
    """
    Threat intel indicators pulled from real feeds (AbuseIPDB, AlienVault OTX)
    plus CVE records pulled from NVD. Used by the correlation engine to enrich
    and auto-triage simulated/ingested alerts.
    """
    __tablename__ = "iocs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(IOCType), nullable=False)
    value = Column(String, nullable=False, index=True)   # IP, domain, hash, or CVE ID
    source = Column(String, nullable=False)               # "AbuseIPDB", "OTX", "NVD"
    confidence = Column(Float, default=0.0)                # 0-100
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=True)               # for CVEs: CVSS-derived label
    cvss_score = Column(Float, nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
