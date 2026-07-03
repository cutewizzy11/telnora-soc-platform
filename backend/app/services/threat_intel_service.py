"""
Real threat intel ingestion.

Pulls live data from three free/freemium feeds:
  - AbuseIPDB  : malicious IP reputation (requires free API key)
  - AlienVault OTX : community threat intel pulses -> IOCs (requires free API key)
  - NVD (NIST) : recent CVEs (no key required, but a key raises the rate limit)

Every fetcher is defensive: if a key is missing or the feed errors/times out,
it logs and returns an empty list rather than raising, so the platform keeps
working with whatever data is available (and the simulator can fill gaps for
demo purposes).
"""
import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.ioc import IndicatorOfCompromise, IOCType

logger = logging.getLogger("threat_intel")
settings = get_settings()

HTTP_TIMEOUT = 10.0


def _upsert_ioc(db: Session, type_: IOCType, value: str, source: str, **kwargs) -> None:
    existing = (
        db.query(IndicatorOfCompromise)
        .filter(IndicatorOfCompromise.value == value, IndicatorOfCompromise.source == source)
        .first()
    )
    if existing:
        existing.last_seen = datetime.utcnow()
        for k, v in kwargs.items():
            setattr(existing, k, v)
    else:
        db.add(
            IndicatorOfCompromise(
                type=type_,
                value=value,
                source=source,
                **kwargs,
            )
        )


def fetch_abuseipdb(db: Session, limit: int = 100) -> int:
    """Pull the AbuseIPDB 'blacklist' of high-confidence malicious IPs."""
    if not settings.abuseipdb_api_key:
        logger.info("AbuseIPDB API key not set - skipping.")
        return 0
    url = "https://api.abuseipdb.com/api/v2/blacklist"
    headers = {"Key": settings.abuseipdb_api_key, "Accept": "application/json"}
    params = {"limit": limit, "confidenceMinimum": 75}
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json().get("data", [])
    except Exception as exc:  # noqa: BLE001
        logger.warning("AbuseIPDB fetch failed: %s", exc)
        return 0

    count = 0
    for entry in data:
        _upsert_ioc(
            db,
            IOCType.IP,
            entry.get("ipAddress"),
            "AbuseIPDB",
            confidence=float(entry.get("abuseConfidenceScore", 0)),
            description="Reported malicious IP (AbuseIPDB blacklist)",
        )
        count += 1
    db.commit()
    return count


def fetch_otx_pulses(db: Session, limit: int = 20) -> int:
    """Pull recent OTX pulses and flatten their IOC indicators."""
    if not settings.otx_api_key:
        logger.info("OTX API key not set - skipping.")
        return 0
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {"X-OTX-API-KEY": settings.otx_api_key}
    params = {"limit": limit}
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            pulses = resp.json().get("results", [])
    except Exception as exc:  # noqa: BLE001
        logger.warning("OTX fetch failed: %s", exc)
        return 0

    type_map = {
        "IPv4": IOCType.IP,
        "IPv6": IOCType.IP,
        "domain": IOCType.DOMAIN,
        "hostname": IOCType.DOMAIN,
        "FileHash-SHA256": IOCType.HASH,
        "FileHash-MD5": IOCType.HASH,
    }

    count = 0
    for pulse in pulses:
        for indicator in pulse.get("indicators", []):
            mapped_type = type_map.get(indicator.get("type"))
            if not mapped_type:
                continue
            _upsert_ioc(
                db,
                mapped_type,
                indicator.get("indicator"),
                "OTX",
                confidence=70.0,
                description=f"OTX pulse: {pulse.get('name', 'unnamed')}",
            )
            count += 1
    db.commit()
    return count


def fetch_nvd_cves(db: Session, days_back: int = 14) -> int:
    """Pull recently published CVEs from the NVD REST API."""
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    headers = {"apiKey": settings.nvd_api_key} if settings.nvd_api_key else {}
    start = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000")
    params = {
        "pubStartDate": start,
        "pubEndDate": end,
        "resultsPerPage": 50,
    }
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            vulns = resp.json().get("vulnerabilities", [])
    except Exception as exc:  # noqa: BLE001
        logger.warning("NVD fetch failed: %s", exc)
        return 0

    count = 0
    for item in vulns:
        cve = item.get("cve", {})
        cve_id = cve.get("id")
        if not cve_id:
            continue
        descriptions = cve.get("descriptions", [])
        description = next((d["value"] for d in descriptions if d.get("lang") == "en"), None)

        cvss_score = None
        metrics = cve.get("metrics", {})
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if key in metrics and metrics[key]:
                cvss_score = metrics[key][0]["cvssData"].get("baseScore")
                break

        severity = "unknown"
        if cvss_score is not None:
            if cvss_score >= 9:
                severity = "critical"
            elif cvss_score >= 7:
                severity = "high"
            elif cvss_score >= 4:
                severity = "medium"
            else:
                severity = "low"

        _upsert_ioc(
            db,
            IOCType.CVE,
            cve_id,
            "NVD",
            confidence=90.0,
            description=description,
            severity=severity,
            cvss_score=cvss_score,
        )
        count += 1
    db.commit()
    return count


def refresh_all_feeds(db: Session) -> dict:
    """Run every feed fetcher and return a summary of how many IOCs were ingested."""
    return {
        "abuseipdb": fetch_abuseipdb(db),
        "otx": fetch_otx_pulses(db),
        "nvd": fetch_nvd_cves(db),
    }
