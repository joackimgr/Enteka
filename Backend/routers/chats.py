from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from db.schemas import CreateChat, CreateMessage
from db.database import *
from core.utils import authenticate_caller
from core import state

router = APIRouter(tags=["chats"])

@router.get("/users/search")
async def search(query: str = ""):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    result = search_users(state.conn, query)
    return result if result is not None else []

@router.get("/users/suggestions")
async def user_suggestions(authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    user_suggest = get_user_suggestions(state.conn, caller_id)
    return {"auth": True, "suggestions": user_suggest}

@router.post("/chats")
async def chats_post(chat_data: CreateChat, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    result = create_chat(state.conn, caller_id, chat_data.user2_id)
    if result is None:
        return JSONResponse(status_code=500, content={"auth": False, "message": "Failed to create chat."})
    return {"auth": True, "chat": result}

@router.get("/chats")
async def chats_get(authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    chat_list = get_chats_by_user_id(state.conn, caller_id)
    if chat_list is None:
        return {"auth": True, "chats": []}
    formatted_chats = []
    for row in chat_list:
        if row[1] == caller_id:
            other_user_id = row[2]
        else:
            other_user_id = row[1]
        other_username = get_user_by_id(state.conn, other_user_id)
        last_msg = get_last_message_by_chat_id(state.conn, row[0])
        if last_msg:
            formatted_chats.append({
                "chat_id": row[0],
                "other_username": other_username,
                "passkey_hash": row[3],
                "created_at": row[4],
                "last_message": last_msg[0] if last_msg else None,
                "last_image": last_msg[1] if last_msg else None,
                "last_timestamp": last_msg[2].split()[1][:5] if last_msg else None
            })
    return {"auth": True, "chats": formatted_chats}

@router.post("/messages")
async def messages_post(message_data: CreateMessage, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    sender_id = authenticate_caller(state.conn, authorization)
    result = insert_message(state.conn, message_data.chat_id, sender_id, message_data.content)
    if result is None:
        return JSONResponse(status_code=500, content={"auth": False, "message": "Failed to send message."})
    return {"auth": True, "message_id": result}

@router.get("/messages/{chat_id}")
async def messages_get(chat_id: int, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    chat_list = get_messages_by_chat_id(state.conn, chat_id)
    if chat_list is None:
        return {"auth": True, "messages": []}
    messages = [{"id": msg[0], "sender_id": msg[1], "content": msg[2], "image": msg[3], "timestamp": msg[4].split()[1][:5], "is_mine": msg[1] == caller_id} for msg in chat_list]
    return {"auth": True, "messages": messages}