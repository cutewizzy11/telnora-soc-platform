# Telnora SOC Platform

A self-hostable Security Operations Center (SOC) web application for alert triage, incident case management, threat intelligence correlation, and SOC analytics — built as an open-source reference platform for security teams, MSSPs, and researchers.

Built and maintained by **[Telnora Technologies](https://github.com/Telnora-Technologies)**.

---

## Features

- **Alert triage feed** — ingest, filter, and triage security alerts by severity, status, source, and asset, with MITRE ATT&CK tactic/technique tagging.
- **Incident case management** — a Kanban-style case board (Open → In Progress → Contained → Resolved → Closed), assignment, and a comment/timeline thread per incident.
- **Real threat intelligence correlation** — pulls live indicators from **AbuseIPDB** (malicious IP reputation), **AlienVault OTX** (community threat pulses), and **NVD** (CVE feed), and automatically correlates incoming alerts against known-bad IPs to boost risk score and escalate severity.
- **Analytics & SLA reporting** — Mean Time To Detect (MTTD), Mean Time To Resolve (MTTR), and per-severity SLA compliance tracking.
- **Role-based access control** — four built-in roles (`admin`, `soc_lead`, `analyst`, `viewer`) enforced on every API route.
- **Audit log** — every state-changing action (login, alert triage, incident updates, user management, threat intel refresh) is recorded with actor, target, and timestamp.
- **Alert simulator** — generates realistic synthetic alerts (some intentionally matching real threat-intel IOCs) so the platform is fully demoable without needing a live SIEM feed.

## Tech stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Frontend   | React + TypeScript + Vite + Tailwind CSS + Recharts |
| Backend    | Python + FastAPI + SQLAlchemy                |
| Database   | PostgreSQL (SQLite supported for quick local runs) |
| Auth       | JWT (OAuth2 password flow) + bcrypt password hashing |
| Threat intel | AbuseIPDB, AlienVault OTX, NVD (NIST) REST APIs |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a deeper look at the data model and correlation engine.

## Getting started

### Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/Telnora-Technologies/telnora-soc-platform.git
cd telnora-soc-platform
cp .env.example .env        # fill in threat intel API keys if you have them (optional)
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs

Then seed demo data (users, simulated alerts, live threat intel if keys are set):

```bash
docker compose exec backend python -m app.scripts.seed
```

### Option 2: Run locally without Docker

**Backend**

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a virtualenv
cp ../.env.example ../.env   # DATABASE_URL defaults to sqlite:///./soc.db if unset
python -m app.scripts.seed
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

### Threat intel API keys (all optional, free tiers available)

The platform works out of the box with simulated data only. To pull **real** threat intelligence, add free API keys to `.env`:

- **AbuseIPDB** — https://www.abuseipdb.com/account/api
- **AlienVault OTX** — https://otx.alienvault.com/api
- **NVD** — works without a key; request one at https://nvd.nist.gov/developers/request-an-api-key to raise the rate limit

Missing keys are handled gracefully — each feed is simply skipped, and the alert simulator keeps the demo populated.

## Roles

| Role       | Permissions |
|------------|-------------|
| `admin`    | Everything, including user management and audit log |
| `soc_lead` | Manage incidents/alerts, refresh threat intel, view audit log & analytics |
| `analyst`  | Triage alerts, work incidents, add comments |
| `viewer`   | Read-only access across the platform |

## Running tests

```bash
cd backend
pip install -r requirements.txt --break-system-packages
pytest -v
```

## Project structure

```
telnora-soc-platform/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy models (User, Alert, Incident, IOC, AuditLog)
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── core/         # security (JWT/bcrypt) + RBAC dependencies
│   │   ├── routers/      # FastAPI route modules
│   │   ├── services/     # threat intel fetchers, correlation engine, alert simulator
│   │   └── scripts/      # seed.py — demo data bootstrap
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/        # Dashboard, Alerts, Incidents, Threat Intel, Analytics, Admin, Audit Log
│       ├── components/   # Layout, SeverityBadge, StatCard, ProtectedRoute
│       └── context/      # AuthContext (JWT session state)
├── docker-compose.yml
└── .env.example
```

## Roadmap / ideas for contributors

- Alembic migrations (currently schema is created via `Base.metadata.create_all`)
- WebSocket push for live alert updates instead of polling
- Additional threat feeds (MISP, Shodan, VirusTotal)
- SOAR-style automated playbooks (auto-block IOC IPs at a firewall API)
- Multi-tenant org support

## License

MIT — see [`LICENSE`](LICENSE). Free to use, fork, and adapt.

---

<sub>Built by [Telnora Technologies](https://github.com/Telnora-Technologies) as an open-source SOC platform for the security community.</sub>
