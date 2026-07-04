# Backlog

Running list of the next real improvements for the SOC platform. Each item should be picked up one at a time, actually implemented (not stubbed), tested where it makes sense, and checked off in the same commit that lands it.

- [x] Add pagination to `GET /alerts` and `GET /incidents` list endpoints
- [x] Add basic rate limiting middleware to public API endpoints
- [ ] Add CSV export endpoint for incidents and alerts
- [ ] Add a dark mode toggle to the frontend
- [ ] Add a GitHub Actions CI workflow (lint + backend tests on push/PR)
- [ ] Add Docker healthchecks to `docker-compose.yml` services
- [ ] Add unit tests for `correlation.py` scoring logic
- [ ] Add unit tests for `threat_intel_service.py` caching behavior
- [ ] Add integration tests for the incidents router (create/update/state transitions)
- [ ] Add request/response OpenAPI examples to routers for better Swagger docs
- [ ] Add loading/skeleton states to the Alerts and Incidents pages
- [ ] Add an error boundary + toast notifications for API errors on the frontend
- [ ] Add a password reset flow (backend endpoint + frontend page)
- [ ] Add actor/date-range filtering to the Audit Log page
- [ ] Add an MTTR/MTTD trend chart (time series) to the Analytics page
- [ ] Add webhook notifications (Slack/Discord) for high-severity alerts
- [ ] Add `.github/ISSUE_TEMPLATE` and `CONTRIBUTING.md`
- [ ] Add retry/backoff handling for the AbuseIPDB/OTX/NVD API clients
- [ ] Add role-based UI hiding (viewer role shouldn't see admin nav items)
- [ ] Add real screenshots to the README (`docs/screenshots/`)
