from datetime import datetime
from pydantic import BaseModel

from app.models.ioc import IOCType


class IOCOut(BaseModel):
    id: str
    type: IOCType
    value: str
    source: str
    confidence: float
    description: str | None = None
    severity: str | None = None
    cvss_score: float | None = None
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True
