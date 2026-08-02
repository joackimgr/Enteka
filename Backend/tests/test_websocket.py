from starlette.websockets import WebSocketDisconnect


def get_id(app, username, token):
    resp = app.get("/users/search", params={"query": username},
                   headers={"Authorization": f"Bearer {token}"})
    for u in resp.json():
        if u["username"] == username:
            return u["id"]
    raise AssertionError(f"{username} not found")


def make_chat(app, a, b):
    b_id = get_id(app, b["username"], a["token"])
    resp = app.post("/chats", json={"user2_id": b_id}, headers={"Authorization": f"Bearer {a['token']}"})
    return resp.json()["chat"]["chat_id"]


def test_ws_closes_without_valid_token(app, signup):
    signup("ws_b")
    try:
        with app.websocket_connect("/ws/1?token=garbage.token.here") as ws:
            ws.receive_text()
            raise AssertionError("connection should have been rejected")
    except WebSocketDisconnect as e:
        assert e.code == 1008


def test_ws_rejects_non_participant(app, signup):
    a = signup("ws_c")
    b = signup("ws_d")
    c = signup("ws_e")
    chat_id = make_chat(app, a, b)
    try:
        with app.websocket_connect(f"/ws/{chat_id}?token={c['token']}") as ws:
            ws.receive_text()
            raise AssertionError("connection should have been rejected")
    except WebSocketDisconnect as e:
        assert e.code == 1008


def test_ws_message_broadcast(app, signup):
    a = signup("ws_f")
    b = signup("ws_g")
    chat_id = make_chat(app, a, b)

    with app.websocket_connect(f"/ws/{chat_id}?token={a['token']}") as ws_a, \
         app.websocket_connect(f"/ws/{chat_id}?token={b['token']}") as ws_b:
        ws_a.send_json({"type": "message", "content": "hello via ws"})
        msg = ws_b.receive_json()
        assert msg["type"] == "new_message"
        assert msg["content"] == "hello via ws"
        assert msg["username"] == a["username"]


def test_ws_typing_excludes_sender(app, signup):
    a = signup("ws_h")
    b = signup("ws_i")
    chat_id = make_chat(app, a, b)

    with app.websocket_connect(f"/ws/{chat_id}?token={a['token']}") as ws_a, \
         app.websocket_connect(f"/ws/{chat_id}?token={b['token']}") as ws_b:
        ws_a.send_json({"type": "typing"})
        msg = ws_b.receive_json()
        assert msg["type"] == "typing"
        assert msg["username"] == a["username"]


def test_ws_message_persisted(app, signup, auth_headers):
    a = signup("ws_j")
    b = signup("ws_k")
    chat_id = make_chat(app, a, b)

    with app.websocket_connect(f"/ws/{chat_id}?token={a['token']}") as ws_a, \
         app.websocket_connect(f"/ws/{chat_id}?token={b['token']}") as ws_b:
        ws_a.send_json({"type": "message", "content": "persist me"})
        ws_b.receive_json()

    # after disconnect, message should be fetchable via REST
    resp = app.get(f"/messages/{chat_id}", headers=auth_headers(a["token"]))
    assert resp.status_code == 200
    msgs = resp.json()["messages"]
    assert any(m["content"] == "persist me" for m in msgs)


def test_ws_voip_forward(app, signup):
    a = signup("ws_l")
    b = signup("ws_m")
    chat_id = make_chat(app, a, b)

    with app.websocket_connect(f"/ws/{chat_id}?token={a['token']}") as ws_a, \
         app.websocket_connect(f"/ws/{chat_id}?token={b['token']}") as ws_b:
        ws_a.send_json({"type": "call_offer", "data": {"sdp": "offer-sdp"}})
        msg = ws_b.receive_json()
        assert msg["type"] == "call_offer"
        assert msg["data"]["sdp"] == "offer-sdp"

        ws_b.send_json({"type": "call_answer", "data": {"sdp": "answer-sdp"}})
        msg = ws_a.receive_json()
        assert msg["type"] == "call_answer"
        assert msg["data"]["sdp"] == "answer-sdp"

        ws_a.send_json({"type": "ice_candidate", "data": {"candidate": "cand-1"}})
        msg = ws_b.receive_json()
        assert msg["type"] == "ice_candidate"
        assert msg["data"]["candidate"] == "cand-1"
