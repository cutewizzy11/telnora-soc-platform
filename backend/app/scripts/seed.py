"""
Seed script: creates default users (one per role), fetches real threat intel
(if API keys are configured), and generates simulated alerts + a couple of
demo incidents so the app looks alive immediately after setup.

Run with:  python -m app.scripts.seed
"""
import random

from app.database import Base, engine, SessionLocal
from app.models.user import User, Role
from app.models.alert import Alert, AlertStatus
from app.models.incident import Incident, IncidentSeverity, IncidentComment
from app.core.security import hash_password
from app.services.threat_intel_service import refresh_all_feeds
from app.services.alert_simulator import generate_alerts


DEFAULT_USERS = [
    ("admin@telnora.io", "Ada Admin", Role.ADMIN, "ChangeMe123!"),
    ("lead@telnora.io", "Sam SOC-Lead", Role.SOC_LEAD, "ChangeMe123!"),
    ("analyst@telnora.io", "Alex Analyst", Role.ANALYST, "ChangeMe123!"),
    ("viewer@telnora.io", "Vic Viewer", Role.VIEWER, "ChangeMe123!"),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Seeding users...")
        users_by_role = {}
        for email, name, role, password in DEFAULT_USERS:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                users_by_role[role] = existing
                continue
            user = User(email=email, full_name=name, role=role, hashed_password=hash_password(password))
            db.add(user)
            db.flush()
            users_by_role[role] = user
        db.commit()

        print("Fetching real threat intel feeds (AbuseIPDB / OTX / NVD)...")
        summary = refresh_all_feeds(db)
        print(f"  -> {summary}")

        print("Generating simulated alerts...")
        alerts = generate_alerts(db, count=40)
        print(f"  -> {len(alerts)} alerts created")

        # Triage a portion of alerts so MTTD/SLA metrics have data.
        for a in random.sample(alerts, k=min(20, len(alerts))):
            a.status = AlertStatus.TRIAGED
            from datetime import timedelta
            a.triaged_at = a.created_at + timedelta(minutes=random.randint(5, 200))
        db.commit()

        print("Creating demo incidents...")
        analyst = users_by_role.get(Role.ANALYST)
        escalated = [a for a in alerts if a.severity.value in ("critical", "high")][:5]
        if escalated:
            incident = Incident(
                title="Suspected credential compromise - multiple hosts",
                summary="Cluster of high/critical alerts correlated to known-malicious infrastructure.",
                severity=IncidentSeverity.CRITICAL,
                assignee_id=analyst.id if analyst else None,
            )
            db.add(incident)
            db.flush()
            for a in escalated:
                a.incident_id = incident.id
            db.add(
                IncidentComment(
                    incident_id=incident.id,
                    author_id=analyst.id if analyst else None,
                    author_name=analyst.full_name if analyst else "System",
                    body="Initial triage complete. Isolating affected hosts and blocking IOC IPs at the firewall.",
                )
            )
            db.commit()

        print("Seed complete.")
        print("Login with: admin@telnora.io / ChangeMe123! (also lead@/analyst@/viewer@telnora.io)")
    finally:
        db.close()


if __name__ == "__main__":
    run()
