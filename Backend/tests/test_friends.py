def get_id(app, username, token):
    resp = app.get("/users/search", params={"query": username},
                   headers={"Authorization": f"Bearer {token}"})
    users = resp.json()
    for u in users:
        if u["username"] == username:
            return u["id"]
    raise AssertionError(f"{username} not found")


def test_send_friend_request(app, signup, auth_headers):
    a = signup("fr_a")
    b = signup("fr_b")
    b_id = get_id(app, "fr_b", a["token"])
    resp = app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    assert resp.json() == {"auth": True, "message": "Friend request sent."}


def test_send_friend_request_to_self_blocked(app, signup, auth_headers):
    a = signup("fr_self")
    resp = app.post(f"/friends/request/1", headers=auth_headers(a["token"]))
    assert resp.status_code == 409


def test_send_duplicate_friend_request(app, signup, auth_headers):
    a = signup("fr_c")
    b = signup("fr_d")
    b_id = get_id(app, "fr_d", a["token"])
    assert app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"])).status_code == 200
    resp = app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"]))
    assert resp.status_code == 409


def test_accept_friend_request(app, signup, auth_headers):
    a = signup("fr_e")
    b = signup("fr_f")
    b_id = get_id(app, "fr_f", a["token"])
    assert app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"])).status_code == 200

    resp = app.get("/friends/requests", headers=auth_headers(b["token"]))
    requests = resp.json()["requests"]
    assert len(requests) == 1
    req_id = requests[0]["id"]

    resp = app.post(f"/friends/accept/{req_id}", headers=auth_headers(b["token"]))
    assert resp.status_code == 200
    assert resp.json()["auth"] is True

    friends = app.get("/friends", headers=auth_headers(a["token"])).json()["friends"]
    assert any(f["friend_id"] == b_id for f in friends)


def test_cannot_accept_others_request(app, signup, auth_headers):
    a = signup("fr_g")
    b = signup("fr_h")
    c = signup("fr_i")
    b_id = get_id(app, "fr_h", a["token"])
    assert app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"])).status_code == 200

    resp = app.get("/friends/requests", headers=auth_headers(b["token"]))
    req_id = resp.json()["requests"][0]["id"]

    # user c (not the recipient) tries to accept
    resp = app.post(f"/friends/accept/{req_id}", headers=auth_headers(c["token"]))
    assert resp.status_code == 404


def test_reject_friend_request(app, signup, auth_headers):
    a = signup("fr_j")
    b = signup("fr_k")
    b_id = get_id(app, "fr_k", a["token"])
    assert app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"])).status_code == 200

    resp = app.get("/friends/requests", headers=auth_headers(b["token"]))
    req_id = resp.json()["requests"][0]["id"]

    resp = app.post(f"/friends/reject/{req_id}", headers=auth_headers(b["token"]))
    assert resp.status_code == 200

    pending = app.get("/friends/requests", headers=auth_headers(b["token"])).json()["requests"]
    assert len(pending) == 0


def test_delete_friend(app, signup, auth_headers):
    a = signup("fr_l")
    b = signup("fr_m")
    b_id = get_id(app, "fr_m", a["token"])
    assert app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"])).status_code == 200
    req_id = app.get("/friends/requests", headers=auth_headers(b["token"])).json()["requests"][0]["id"]
    assert app.post(f"/friends/accept/{req_id}", headers=auth_headers(b["token"])).status_code == 200

    resp = app.delete(f"/friends/{b_id}", headers=auth_headers(a["token"]))
    assert resp.status_code == 200

    friends = app.get("/friends", headers=auth_headers(a["token"])).json()["friends"]
    assert all(f["friend_id"] != b_id for f in friends)


def test_friends_search_only_accepted(app, signup, auth_headers):
    a = signup("fr_n")
    b = signup("fr_o")
    c = signup("fr_p")
    b_id = get_id(app, "fr_o", a["token"])
    assert app.post(f"/friends/request/{b_id}", headers=auth_headers(a["token"])).status_code == 200
    req_id = app.get("/friends/requests", headers=auth_headers(b["token"])).json()["requests"][0]["id"]
    assert app.post(f"/friends/accept/{req_id}", headers=auth_headers(b["token"])).status_code == 200

    resp = app.get("/friends/search", params={"query": "fr_p"}, headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    assert resp.json()["friends"] == []

    resp = app.get("/friends/search", params={"query": "fr_o"}, headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    names = [f["username"] for f in resp.json()["friends"]]
    assert "fr_o" in names
