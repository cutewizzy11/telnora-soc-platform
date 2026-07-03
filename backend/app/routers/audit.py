from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import require_roles
from app.models.audit import AuditLog
from app.models.user import User, Role
from app.schemas.audit import AuditLogOut

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN, Role.SOC_LEAD)),
):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
