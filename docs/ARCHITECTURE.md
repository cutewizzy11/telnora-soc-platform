# Architecture

## Overview

Telnora SOC Platform is a two-tier application: a FastAPI backend exposing a
REST API, and a React SPA frontend. There is no separate message queue or
metrics store — at the scale this project targets (a SOC team, not a global
MSSP), computing analytics directly from the relational tables is simpler
and more transparent than standing up additional infrastructure.

```
┌─────────────┐        HTTPS/JSON        ┌──────────────────┐        ┌────────────┐
│   React SPA │  <-------------------->  │  FastAPI backend  │ <----> │ PostgreSQL │
│  (Vite, TS) │                          │  (JWT + RBAC)     │        └────────────┘
└─────────────┘                          └────────┬─────────┘
                                                   │
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                              AbuseIPDB          OTX            NVD
                             (IP reputation)  (community IOCs) (CVE feed)
```

## Data model

- **User** — email/password (bcrypt), one of four roles (`admin`, `soc_lead`, `analyst`, `viewer`).
- **Alert** — a single detection event (title, source, severity, status, src/dest IP, MITRE ATT&CK tags, risk score, optional `ioc_match`). Alerts can be attached to an Incident.
- **Incident** — a case grouping one or more related alerts, with its own severity/status lifecycle, an assignee, and a comment timeline.
- **IndicatorOfCompromise (IOC)** — threat intel records: IPs/domains/hashes from AbuseIPDB & OTX, or CVEs from NVD. Deduplicated by `(value, source)`.
- **AuditLog** — append-only record of every state-changing action, keyed by actor + action + target.

## Correlation engine

`app/services/correlation.py` is intentionally simple: it looks up an alert's
`src_ip`/`dest_ip` against the IOC table. On a match it:

1. Stamps `ioc_match` with `"{source}:{value}"`.
2. Raises `risk_score` to at least the IOC's confidence score.
3. Escalates severity by one or two steps depending on confidence (a
   90+ confidence match can jump an alert from `low` straight to `critical`).

This mirrors, at a small scale, what a real SIEM correlation rule or
enrichment pipeline does — enough to demonstrate the concept without needing
a rules DSL or streaming engine.

## Threat intel ingestion

`app/services/threat_intel_service.py` has one function per feed
(`fetch_abuseipdb`, `fetch_otx_pulses`, `fetch_nvd_cves`), all called by
`refresh_all_feeds()`. Every fetcher:

- Reads its API key from settings (env var); if absent, logs and returns `0` immediately.
- Wraps the HTTP call in a try/except so a feed outage never crashes the request.
- Upserts into the `iocs` table keyed by `(value, source)`.

This means the platform degrades gracefully with zero configuration (the
alert simulator fills the gap for demo purposes) and gets progressively more
"real" as you add API keys.

## Auth & RBAC

- Login issues a JWT (`app/core/security.py`) containing the user id as `sub`.
- `app/core/deps.py` exposes `get_current_user` (any authenticated user) and
  `require_roles(*roles)` (a dependency factory used to gate specific routes,
  e.g. only `admin` can manage users, only `admin`/`soc_lead` can view the
  audit log or refresh threat intel feeds).

## Why no Alembic (yet)

For a first public release, `Base.metadata.create_all()` on startup is
enough to get a working schema. Alembic migrations are called out in the
README roadmap as a natural next contribution once the schema needs to
evolve without dropping data.
