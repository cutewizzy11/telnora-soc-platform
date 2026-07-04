from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitMiddleware


def _build_app(requests: int, window_seconds: int = 60) -> TestClient:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, requests=requests, window_seconds=window_seconds)

    @app.get("/api/alerts")
    def alerts():
        return {"ok": True}

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return TestClient(app)


def test_requests_within_limit_pass():
    client = _build_app(requests=3)
    for _ in range(3):
        resp = client.get("/api/alerts")
        assert resp.status_code == 200


def test_requests_over_limit_are_throttled():
    client = _build_app(requests=3)
    for _ in range(3):
        assert client.get("/api/alerts").status_code == 200

    resp = client.get("/api/alerts")
    assert resp.status_code == 429
    assert resp.json()["detail"] == "Rate limit exceeded. Please slow down."
    assert "Retry-After" in resp.headers


def test_different_clients_have_independent_limits():
    client = _build_app(requests=1)
    for _ in range(1):
        assert client.get("/api/alerts", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    # Second client (different forwarded IP) should not be throttled yet.
    assert client.get("/api/alerts", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200
    # First client should now be throttled.
    assert client.get("/api/alerts", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 429


def test_exempt_paths_are_never_limited():
    client = _build_app(requests=1)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/health").status_code == 200


def test_zero_requests_disables_limiting():
    client = _build_app(requests=0)
    for _ in range(5):
        assert client.get("/api/alerts").status_code == 200
