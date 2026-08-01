from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from db.database import *
from core.utils import authenticate_caller
from core import state

router = APIRouter(tags=["friends"])

@router.post("/friends/request/{user_id}")
async def request_friends(user_id: int, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    result = send_friend_request(state.conn, caller_id, user_id)
    if result:
        return {"auth": True, "message": "Friend request sent."}
    return JSONResponse(status_code=409, content={"auth": False, "message": "Friend request already sent."})

@router.get("/friends/requests")
async def get_request_friends(authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    requests = get_pending_requests(state.conn, caller_id)
    return {"auth": True, "requests": requests}

@router.post("/friends/accept/{request_id}")
async def accept_friends(request_id: int, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    result = accept_friend_request(state.conn, request_id, caller_id)
    if result:
        return {"auth": True, "message": "Friend request accepted."}
    return JSONResponse(status_code=404, content={"auth": False, "message": "Friend request not found."})

@router.post("/friends/reject/{request_id}")
async def reject_friends(request_id: int, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    result = reject_friend_request(state.conn, request_id, caller_id)
    if result:
        return {"auth": True, "message": "Friend request rejected."}
    return JSONResponse(status_code=404, content={"auth": False, "message": "Friend request not found."})

@router.get("/friends")
async def get_friends_list(authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    friends = get_friends(state.conn, caller_id)
    return {"auth": True, "friends": friends}

@router.delete("/friends/{friend_id}")
async def remove_friends(friend_id: int, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    result = remove_friend(state.conn, caller_id, friend_id)
    if result:
        return {"auth": True, "message": "Friend removed."}
    return JSONResponse(status_code=404, content={"auth": False, "message": "Friend not found."})

@router.get("/friends/search")
async def search_friendslist(query: str = "", authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    if not query:
        return {"auth": True, "friends": []}
    friends = search_friends(state.conn, caller_id, query)
    return {"auth": True, "friends": friends}