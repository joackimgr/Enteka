from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from db.database import get_user_by_username, insert_message, chat_belongs_to_user, get_other_participant
from security.auth import verify_token
from datetime import datetime
from core import state

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/notifications")
async def notification_endpoint(websocket: WebSocket, token: str = Query()):
    try:
        payload = verify_token(token)
    except HTTPException:
        await websocket.accept()
        await websocket.close(code=1008)
        return
    username = payload["sub"]
    caller_id = get_user_by_username(state.conn, username)
    if caller_id is None:
        await websocket.accept()
        await websocket.close(code=1008)
        return

    await state.notification_manager.connect(websocket, caller_id)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        state.notification_manager.disconnect(websocket, caller_id)

@router.websocket("/ws/{chat_id}")
async def webSocket_endpoint(websocket: WebSocket, chat_id: int, token: str = Query()):
    if state.conn is not None:
        try:
            payload = verify_token(token)
        except HTTPException:
            await websocket.accept()
            await websocket.close(code=1008)
            return None
        username = payload["sub"]
        caller_id = get_user_by_username(state.conn, username)
        if caller_id is None:
            await websocket.accept()
            await websocket.close(code=1008)
            return
        if chat_belongs_to_user(state.conn, chat_id, caller_id):
            await state.manager.connect(websocket, chat_id)
        else:
            await websocket.accept()
            await websocket.close(code=1008)
            return
        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "message")
                if msg_type == "message":
                    content = data["content"]
                    message_id = insert_message(state.conn, chat_id, caller_id, content)
                    await state.manager.broadcast({"type": "new_message",
                                                  "message_id": message_id,
                                                  "caller_id": caller_id,
                                                  "username": username,
                                                  "content": content,
                                                  "image_url": None,
                                                  "timestamp": datetime.now().strftime("%H:%M")
                                                  }, chat_id)
                    other_user_id = get_other_participant(state.conn, chat_id, caller_id)
                    if other_user_id:
                        await state.notification_manager.send_to_user(
                            {"type": "new_message", "chat_id": chat_id}, other_user_id
                        )
                elif msg_type == "image":
                    content = data.get("content", "")
                    image_url = data.get("image_url")
                    message_id = insert_message(state.conn, chat_id, caller_id, content, image_url)
                    await state.manager.broadcast({"type": "new_message",
                                                  "message_id": message_id,
                                                  "caller_id": caller_id,
                                                  "username": username,
                                                  "content": content,
                                                  "image_url": image_url,
                                                  "timestamp": datetime.now().strftime("%H:%M")
                                                }, chat_id)
                    other_user_id = get_other_participant(state.conn, chat_id, caller_id)
                    if other_user_id:
                        await state.notification_manager.send_to_user(
                            {"type": "new_message", "chat_id": chat_id}, other_user_id
                        )
                elif msg_type == "typing":
                    await state.manager.broadcast({"type": "typing", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "stop_typing":
                    await state.manager.broadcast({"type": "stop_typing", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "call_offer":
                    await state.manager.broadcast({"type": "call_offer", "username": username, "data": data.get("data")}, chat_id, exclude=websocket)
                elif msg_type == "call_answer":
                    await state.manager.broadcast({"type": "call_answer", "username": username, "data": data.get("data")}, chat_id, exclude=websocket)
                elif msg_type == "ice_candidate":
                    await state.manager.broadcast({"type": "ice_candidate", "username": username, "data": data.get("data")}, chat_id, exclude=websocket)
                elif msg_type == "call_end":
                    await state.manager.broadcast({"type": "call_end", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "call_reject":
                    await state.manager.broadcast({"type": "call_reject", "username": username}, chat_id, exclude=websocket)
        except WebSocketDisconnect:
            state.manager.disconnect(websocket, chat_id)
