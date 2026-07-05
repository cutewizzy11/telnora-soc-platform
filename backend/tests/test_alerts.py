def test_create_and_list_alert(client, auth_headers):
    payload = {
        "title": "Suspicious login",
        "source": "IDS/IPS",
        "severity": "high",
        "src_ip": "203.0.113.5",
    }
    resp = client.post("/api/alerts", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    alert = resp.json()
    assert alert["title"] == "Suspicious login"
    assert alert["status"] == "new"

    list_resp = client.get("/api/alerts", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_correlation_escalates_severity(client, auth_headers, db_session):
    from app.models.ioc import IndicatorOfCompromise, IOCType

    ioc = IndicatorOfCompromise(type=IOCType.IP, value="198.51.100.7", source="AbuseIPDB", confidence=95.0)
    db_session.add(ioc)
    db_session.commit()

    payload = {"title": "Odd traffic", "source": "Firewall", "severity": "low", "src_ip": "198.51.100.7"}
    resp = client.post("/api/alerts", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    alert = resp.json()
    assert alert["ioc_match"] is not None
    assert alert["severity"] in ("high", "critical")


def test_update_alert_status_sets_triaged_at(client, auth_headers):
    payload = {"title": "Test alert", "source": "EDR", "severity": "medium"}
    created = client.post("/api/alerts", json=payload, headers=auth_headers).json()

    resp = client.patch(f"/api/alerts/{created['id']}", json={"status": "triaged"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["triaged_at"] is not None


def test_analytics_summary_endpoint(client, auth_headers):
    client.post("/api/alerts", json={"title": "A", "source": "EDR", "severity": "critical"}, headers=auth_headers)
    resp = client.get("/api/analytics/summary", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_alerts"] == 1
    assert body["alerts_by_severity"]["critical"] == 1


def test_list_alerts_pagination(client, auth_headers):
    for i in range(5):
        client.post(
            "/api/alerts",
            json={"title": f"Alert {i}", "source": "EDR", "severity": "low"},
            headers=auth_headers,
        )

    first_page = client.get("/api/alerts", params={"limit": 2, "offset": 0}, headers=auth_headers)
    assert first_page.status_code == 200
    assert len(first_page.json()) == 2
    assert first_page.headers["x-total-count"] == "5"

    second_page = client.get("/api/alerts", params={"limit": 2, "offset": 2}, headers=auth_headers)
    assert len(second_page.json()) == 2
    assert second_page.headers["x-total-count"] == "5"

    first_ids = {a["id"] for a in first_page.json()}
    second_ids = {a["id"] for a in second_page.json()}
    assert first_ids.isdisjoint(second_ids)

    last_page = client.get("/api/alerts", params={"limit": 2, "offset": 4}, headers=auth_headers)
    assert len(last_page.json()) == 1


def test_viewer_role_cannot_create_alert(client, db_session):
    from app.models.user import User, Role
    from app.core.security import hash_password

    viewer = User(
        email="viewer@test.io", full_name="Viewer", role=Role.VIEWER, hashed_password=hash_password("pw123456")
    )
    db_session.add(viewer)
    db_session.commit()

    from fastapi.testclient import TestClient
    login = client.post("/api/auth/login", data={"username": "viewer@test.io", "password": "pw123456"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = client.post("/api/alerts", json={"title": "X", "source": "EDR"}, headers=headers)
    assert resp.status_code == 403


def test_export_alerts_csv(client, auth_headers):
    client.post(
        "/api/alerts",
        json={"title": "Suspicious login", "source": "IDS/IPS", "severity": "high", "src_ip": "203.0.113.5"},
        headers=auth_headers,
    )
    client.post(
        "/api/alerts",
        json={"title": "Port scan", "source": "Firewall", "severity": "low"},
        headers=auth_headers,
    )

    resp = client.get("/api/alerts/export", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=" in resp.headers["content-disposition"]

    lines = resp.text.strip().splitlines()
    assert lines[0].split(",")[:3] == ["id", "title", "description"]
    assert len(lines) == 3  # header + 2 alerts
    assert "Suspicious login" in resp.text
    assert "Port scan" in resp.text


def test_export_alerts_csv_respects_filters(client, auth_headers):
    client.post(
        "/api/alerts",
        json={"title": "Critical one", "source": "EDR", "severity": "critical"},
        headers=auth_headers,
    )
    client.post(
        "/api/alerts",
        json={"title": "Low one", "source": "EDR", "severity": "low"},
        headers=auth_headers,
    )

    resp = client.get("/api/alerts/export", params={"severity": "critical"}, headers=auth_headers)
    assert resp.status_code == 200
    lines = resp.text.strip().splitlines()
    assert len(lines) == 2  # header + 1 matching alert
    assert "Critical one" in resp.text
    assert "Low one" not in resp.text
