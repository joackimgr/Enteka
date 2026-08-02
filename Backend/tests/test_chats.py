import pytest


def make_chat(app, user1, user2, headers):
    user2_id = get_user_id(app, user2["username"], user1["token"])
    resp = app.post("/chats", json={"user2_id": user2_id}, headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["auth"] is True
    return data["chat"]


def get_user_id(app, username, token):
    resp = app.get("/users/search", params={"query": username}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    users = resp.json()
    for u in users:
        if u["username"] == username:
            return u["id"]
    raise AssertionError(f"{username} not found in search results")
def test_create_chat(app, signup, auth_headers):
    a = signup("chat_a")
    b = signup("chat_b")
    headers = auth_headers(a["token"])
    b_id = get_user_id(app, "chat_b", a["token"])
    chat = make_chat(app, a, b, headers)
    assert chat["chat_id"] > 0
    assert chat["passkey_hash"]


def test_create_chat_with_nonexistent_user_404(app, signup, auth_headers):
    a = signup("chat_a2")
    headers = auth_headers(a["token"])
    resp = app.post("/chats", json={"user2_id": 999999}, headers=headers)
    assert resp.status_code == 404


def test_create_chat_duplicate_returns_same_chat(app, signup, auth_headers):
    a = signup("chat_a3")
    b = signup("chat_b3")
    headers = auth_headers(a["token"])
    b_id = get_user_id(app, "chat_b3", a["token"])
    first = make_chat(app, a, b, headers)
    resp = app.post("/chats", json={"user2_id": b_id}, headers=headers)
    assert resp.status_code == 200
    second = resp.json()["chat"]
    assert first["chat_id"] == second["chat_id"]


def test_create_chat_requires_auth(app):
    resp = app.post("/chats", json={"user2_id": 1})
    assert resp.status_code == 401


def test_get_chats_empty(app, signup, auth_headers):
    a = signup("chat_a4")
    resp = app.get("/chats", headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    assert resp.json() == {"auth": True, "chats": []}


def test_send_and_get_messages(app, signup, auth_headers):
    a = signup("chat_a5")
    b = signup("chat_b5")
    headers = auth_headers(a["token"])
    b_id = get_user_id(app, "chat_b5", a["token"])
    chat = make_chat(app, a, b, headers)
    chat_id = chat["chat_id"]

    resp = app.post("/messages", json={"chat_id": chat_id, "content": "hello there"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["auth"] is True

    resp = app.get(f"/messages/{chat_id}", headers=headers)
    assert resp.status_code == 200
    msgs = resp.json()["messages"]
    assert len(msgs) == 1
    assert msgs[0]["content"] == "hello there"
    assert msgs[0]["is_mine"] is True


def test_messages_empty_chat(app, signup, auth_headers):
    a = signup("chat_a6")
    b = signup("chat_b6")
    headers = auth_headers(a["token"])
    b_id = get_user_id(app, "chat_b6", a["token"])
    chat = make_chat(app, a, b, headers)
    resp = app.get(f"/messages/{chat['chat_id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"auth": True, "messages": []}


def test_messages_forbidden_for_non_participant(app, signup, auth_headers):
    a = signup("chat_a7")
    b = signup("chat_b7")
    c = signup("chat_c7")
    headers_a = auth_headers(a["token"])
    headers_c = auth_headers(c["token"])
    b_id = get_user_id(app, "chat_b7", a["token"])
    chat = make_chat(app, a, b, headers_a)
    chat_id = chat["chat_id"]

    resp = app.get(f"/messages/{chat_id}", headers=headers_c)
    assert resp.status_code == 403

    resp = app.post("/messages", json={"chat_id": chat_id, "content": "intruder"}, headers=headers_c)
    assert resp.status_code == 403


def test_messages_requires_auth(app, signup, auth_headers):
    a = signup("chat_a8")
    resp = app.get("/messages/1")
    assert resp.status_code == 401


def test_search_users_requires_auth(app):
    resp = app.get("/users/search", params={"query": "a"})
    assert resp.status_code == 401


def test_search_users_finds_matching(app, signup, auth_headers):
    a = signup("zebra_search")
    signup("zebra_target")
    resp = app.get("/users/search", params={"query": "zebra_tar"}, headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    names = [u["username"] for u in resp.json()]
    assert "zebra_target" in names


def test_search_users_empty_results(app, signup, auth_headers):
    a = signup("lone_ranger")
    resp = app.get("/users/search", params={"query": "no_such_user"}, headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    assert resp.json() == []


def test_suggestions_exclude_self(app, signup, auth_headers):
    a = signup("sug_a")
    signup("sug_b")
    signup("sug_c")
    resp = app.get("/users/suggestions", headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["auth"] is True
    usernames = [s["username"] for s in data["suggestions"]]
    assert "sug_a" not in usernames
