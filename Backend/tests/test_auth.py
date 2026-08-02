def test_health(app):
    resp = app.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Backend is working!"}


def test_signup_success(app):
    resp = app.post("/signup", json={
        "username": "alice",
        "email": "alice@test.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["auth"] is True
    assert "token" in data


def test_signup_duplicate_username(app):
    payload = {"username": "bob", "email": "bob@test.com", "password": "password123"}
    assert app.post("/signup", json=payload).status_code == 200
    resp = app.post("/signup", json=payload)
    assert resp.status_code == 409
    assert resp.json()["auth"] is False


def test_signup_duplicate_email(app):
    first = {"username": "carol", "email": "shared@test.com", "password": "password123"}
    second = {"username": "dave", "email": "shared@test.com", "password": "password123"}
    assert app.post("/signup", json=first).status_code == 200
    resp = app.post("/signup", json=second)
    assert resp.status_code == 409


def test_login_success(app, signup):
    user = signup("erin")
    resp = app.post("/login", json={"username": user["username"], "password": "password123"})
    assert resp.status_code == 200
    assert resp.json()["auth"] is True
    assert "token" in resp.json()


def test_login_wrong_password(app, signup):
    user = signup("frank")
    resp = app.post("/login", json={"username": user["username"], "password": "wrongpass"})
    assert resp.status_code == 401
    assert resp.json()["auth"] is False


def test_login_unknown_user(app):
    resp = app.post("/login", json={"username": "nobody", "password": "x"})
    assert resp.status_code == 401


def test_verify_valid_token(app, signup):
    user = signup("grace")
    resp = app.post("/verify", json={"token": user["token"]})
    assert resp.status_code == 200
    assert resp.json()["auth"] is True
    assert resp.json()["username"] == "grace"


def test_verify_invalid_token(app):
    resp = app.post("/verify", json={"token": "garbage.token.here"})
    assert resp.status_code == 401
    assert resp.json()["auth"] is False
