"""
Synthetic alert generator.

A real SOC ingests alerts from EDR/SIEM/firewall/IDS tooling. For a public
demo/portfolio build we don't want to require a live SIEM, so this module
generates realistic-looking alerts - some clean, some deliberately using IP
values pulled from the real threat-intel IOC table so the correlation engine
has genuine hits to demonstrate during a demo.
"""
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.models.alert import Alert, Severity, AlertStatus
from app.models.ioc import IndicatorOfCompromise, IOCType
from app.services.correlation import correlate_alert

fake = Faker()

_SOURCES = ["EDR", "Firewall", "IDS/IPS", "Cloud (AWS GuardDuty)", "Email Gateway", "DNS Sinkhole"]
_ASSETS = ["WIN-DC01", "WEB-PROD-03", "db-primary-01", "vpn-gateway", "corp-laptop-114", "k8s-node-07"]

_TEMPLATES = [
    ("Suspicious PowerShell execution", "critical", "TA0002", "T1059.001"),
    ("Multiple failed login attempts", "medium", "TA0006", "T1110"),
    ("Outbound connection to known-bad IP", "high", "TA0011", "T1071"),
    ("Unusual data exfiltration volume", "critical", "TA0010", "T1041"),
    ("Malware signature detected", "high", "TA0002", "T1204"),
    ("Port scan detected", "low", "TA0043", "T1595"),
    ("Privilege escalation attempt", "critical", "TA0004", "T1068"),
    ("Phishing email quarantined", "medium", "TA0001", "T1566"),
    ("Unexpected admin account created", "high", "TA0003", "T1136"),
    ("DNS query to newly registered domain", "low", "TA0011", "T1568"),
]


def _random_ip() -> str:
    return fake.ipv4_public()


def generate_alerts(db: Session, count: int = 25, use_real_iocs_ratio: float = 0.3) -> list[Alert]:
    known_bad_ips = [
        row.value
        for row in db.query(IndicatorOfCompromise).filter(IndicatorOfCompromise.type == IOCType.IP).all()
    ]

    created = []
    for _ in range(count):
        title, sev, tactic, technique = random.choice(_TEMPLATES)
        use_bad_ip = known_bad_ips and random.random() < use_real_iocs_ratio

        alert = Alert(
            title=title,
            description=fake.sentence(nb_words=12),
            source=random.choice(_SOURCES),
            severity=Severity(sev),
            status=AlertStatus.NEW,
            src_ip=random.choice(known_bad_ips) if use_bad_ip else _random_ip(),
            dest_ip=_random_ip(),
            asset=random.choice(_ASSETS),
            mitre_tactic=tactic,
            mitre_technique=technique,
            risk_score=float(random.randint(10, 60)),
            created_at=datetime.utcnow() - timedelta(minutes=random.randint(0, 60 * 24 * 3)),
        )
        correlate_alert(db, alert)
        db.add(alert)
        created.append(alert)

    db.commit()
    for a in created:
        db.refresh(a)
    return created
