from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.ioc import IndicatorOfCompromise, IOCType
from app.models.user import User, Role
from app.schemas.ioc import IOCOut
from app.services.threat_intel_service import refresh_all_feeds
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/threat-intel", tags=["threat-intel"])


@router.get("/iocs", response_model=list[IOCOut])
def list_iocs(
    type: IOCType | None = None,
    q: str | None = Query(None, description="Search by value (IP/domain/hash/CVE)"),
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(IndicatorOfCompromise)
    if type:
        query = query.filter(IndicatorOfCompromise.type == type)
    if q:
        query = query.filter(IndicatorOfCompromise.value.ilike(f"%{q}%"))
    return query.order_by(IndicatorOfCompromise.last_seen.desc()).limit(limit).all()


@router.post("/refresh", summary="Fetch latest data from AbuseIPDB, OTX, and NVD")
def refresh_feeds(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD)),
):
    summary = refresh_all_feeds(db)
    log_action(db, user, "threat_intel.refresh", details=str(summary))
    return summary
