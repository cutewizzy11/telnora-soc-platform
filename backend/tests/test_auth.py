def test_login_success(client, admin_user):
    resp = client.post("/api/auth/login", data={"username": admin_user.email, "password": "password123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == admin_user.email


def test_login_wrong_password(client, admin_user):
    resp = client.post("/api/auth/login", data={"username": admin_user.email, "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers, admin_user):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == admin_user.email
