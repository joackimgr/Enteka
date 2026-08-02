def test_get_me(app, signup, auth_headers):
    user = signup("set_a")
    resp = app.get("/users/me", headers=auth_headers(user["token"]))
    assert resp.status_code == 200
    profile = resp.json()["profile"]
    assert profile["username"] == "set_a"
    assert profile["email"] == "set_a@test.com"
    assert profile["profile_picture"] is None


def test_get_me_requires_auth(app):
    resp = app.get("/users/me")
    assert resp.status_code == 401


def test_update_username(app, signup, auth_headers):
    user = signup("set_b")
    headers = auth_headers(user["token"])
    resp = app.put("/users/me/username", json={"username": "set_b_renamed"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["auth"] is True
    assert data["username"] == "set_b_renamed"
    assert "token" in data
    # fresh token must be usable
    resp = app.get("/users/me", headers=auth_headers(data["token"]))
    assert resp.status_code == 200
    assert resp.json()["profile"]["username"] == "set_b_renamed"


def test_update_username_collision(app, signup, auth_headers):
    a = signup("set_c")
    b = signup("set_d")
    resp = app.put("/users/me/username", json={"username": "set_d"}, headers=auth_headers(a["token"]))
    assert resp.status_code == 409


def test_update_email(app, signup, auth_headers):
    user = signup("set_e")
    resp = app.put("/users/me/email", json={"email": "newmail@test.com"}, headers=auth_headers(user["token"]))
    assert resp.status_code == 200
    assert resp.json()["auth"] is True
    profile = app.get("/users/me", headers=auth_headers(user["token"])).json()["profile"]
    assert profile["email"] == "newmail@test.com"


def test_update_email_collision(app, signup, auth_headers):
    a = signup("set_f")
    b = signup("set_g")
    resp = app.put("/users/me/email", json={"email": "set_g@test.com"}, headers=auth_headers(a["token"]))
    assert resp.status_code == 409


def test_update_password_wrong_current(app, signup, auth_headers):
    user = signup("set_h")
    resp = app.put("/users/me/password",
                   json={"current_password": "wrong", "new_password": "newpass123"},
                   headers=auth_headers(user["token"]))
    assert resp.status_code == 401


def test_update_password_success(app, signup, auth_headers):
    user = signup("set_i")
    resp = app.put("/users/me/password",
                   json={"current_password": "password123", "new_password": "newpass123"},
                   headers=auth_headers(user["token"]))
    assert resp.status_code == 200
    # old password no longer works, new one does
    assert app.post("/login", json={"username": "set_i", "password": "password123"}).status_code == 401
    assert app.post("/login", json={"username": "set_i", "password": "newpass123"}).status_code == 200


def test_update_profile_picture(app, signup, auth_headers):
    user = signup("set_j")
    resp = app.put("/users/me/profile-picture", json={"image_url": "/uploads/abc123.png"}, headers=auth_headers(user["token"]))
    assert resp.status_code == 200
    assert resp.json()["profile_picture"] == "/uploads/abc123.png"
    profile = app.get("/users/me", headers=auth_headers(user["token"])).json()["profile"]
    assert profile["profile_picture"] == "/uploads/abc123.png"


def test_update_profile_picture_invalid_path(app, signup, auth_headers):
    user = signup("set_k")
    resp = app.put("/users/me/profile-picture", json={"image_url": "https://evil.com/x.png"}, headers=auth_headers(user["token"]))
    assert resp.status_code == 400


def test_settings_require_auth(app):
    cases = [
        ("put", "/users/me/username", {"username": "x"}),
        ("put", "/users/me/email", {"email": "x@test.com"}),
        ("put", "/users/me/password", {"current_password": "a", "new_password": "b"}),
        ("put", "/users/me/profile-picture", {"image_url": "/uploads/a.png"}),
    ]
    for method, path, body in cases:
        resp = getattr(app, method)(path, json=body)
        assert resp.status_code == 401, path
