from fastapi import APIRouter, Header
from database import *
from utils import authenticate_caller
import state

router = APIRouter(tags=["friends"])

@router.post("/friends/request/{user_id}")
async def request_friends(user_id: int, authorization: str = Header(None)):
    if state.conn is not None:
        caller_id, error = authenticate_caller(state.conn, authorization)
        if error:
            return error
        result = send_friend_request(state.conn, caller_id, user_id)
        if result:
            return {"auth": True, "message": "Friend request sent."}
        return {"auth": False, "message": "Friend request already sent."}
    return {"message": "Error! Cannot establish the database connection."}

@router.get("/friends/requests")
async def get_request_friends(authorization: str = Header(None)):
    if state.conn is not None:
        caller_id, error = authenticate_caller(state.conn, authorization)
        if error:
            return error
        requests = get_pending_requests(state.conn, caller_id)
        return {"auth": True, "requests": requests}
    return {"message": "Error! Cannot establish the database connection."}

@router.post("/friends/accept/{request_id}")
async def accept_friends(request_id: int, authorization: str = Header(None)):
    if state.conn is not None:
        _, error = authenticate_caller(state.conn, authorization)
        if error:
            return error
        result = accept_friend_request(state.conn, request_id)
        if result:
            return {"auth": True, "message": "Friend request accepted."}
        return {"auth": False, "message": "Friend request not found."}
    return {"message": "Error! Cannot establish the database connection."}

@router.post("/friends/reject/{request_id}")
async def reject_friends(request_id: int, authorization: str = Header(None)):
    if state.conn is not None:
        _, error = authenticate_caller(state.conn, authorization)
        if error:
            return error
        result = reject_friend_request(state.conn, request_id)
        if result:
            return {"auth": True, "message": "Friend request rejected."}
        return {"auth": False, "message": "Friend request not found."}
    return {"message": "Error! Cannot establish the database connection."}

@router.get("/friends")
async def get_friends_list(authorization: str = Header(None)):
    if state.conn is not None:
        caller_id, error = authenticate_caller(state.conn, authorization)
        if error:
            return error
        friends = get_friends(state.conn, caller_id)
        return {"auth": True, "friends": friends}
    return {"message": "Error! Cannot establish the database connection."}

@router.delete("/friends/{friend_id}")
async def remove_friends(friend_id: int, authorization: str = Header(None)):
    if state.conn is not None:
        caller_id, error = authenticate_caller(state.conn, authorization)
        if error:
            return error
        result = remove_friend(state.conn, caller_id, friend_id)
        if result:
            return {"auth": True, "message": "Friend removed."}
        return {"auth": False, "message": "Friend not found."}
    return {"message": "Error! Cannot establish the database connection."}
