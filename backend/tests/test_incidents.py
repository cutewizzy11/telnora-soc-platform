def test_create_and_list_incident(client, auth_headers):
    payload = {"title": "Ransomware outbreak", "summary": "Multiple hosts encrypted", "severity": "critical"}
    resp = client.post("/api/incidents", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    incident = resp.json()
    assert incident["title"] == "Ransomware outbreak"
    assert incident["status"] == "open"

    list_resp = client.get("/api/incidents", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.headers["x-total-count"] == "1"


def test_list_incidents_pagination(client, auth_headers):
    for i in range(5):
        client.post(
            "/api/incidents",
            json={"title": f"Incident {i}", "summary": "auto", "severity": "medium"},
            headers=auth_headers,
        )

    first_page = client.get("/api/incidents", params={"limit": 2, "offset": 0}, headers=auth_headers)
    assert first_page.status_code == 200
    assert len(first_page.json()) == 2
    assert first_page.headers["x-total-count"] == "5"

    second_page = client.get("/api/incidents", params={"limit": 2, "offset": 2}, headers=auth_headers)
    assert len(second_page.json()) == 2

    first_ids = {i["id"] for i in first_page.json()}
    second_ids = {i["id"] for i in second_page.json()}
    assert first_ids.isdisjoint(second_ids)

    last_page = client.get("/api/incidents", params={"limit": 2, "offset": 4}, headers=auth_headers)
    assert len(last_page.json()) == 1


def test_list_incidents_filters_by_status(client, auth_headers):
    created = client.post(
        "/api/incidents",
        json={"title": "Open one", "summary": "x", "severity": "low"},
        headers=auth_headers,
    ).json()
    client.patch(f"/api/incidents/{created['id']}", json={"status": "resolved"}, headers=auth_headers)
    client.post(
        "/api/incidents",
        json={"title": "Still open", "summary": "x", "severity": "low"},
        headers=auth_headers,
    )

    resp = client.get("/api/incidents", params={"status": "resolved"}, headers=auth_headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Open one"
