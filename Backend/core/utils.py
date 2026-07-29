from fastapi import HTTPException
from security.auth import verify_token
from db.database import get_user_by_username

def authenticate_caller(conn, authorization):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token_parts = authorization.split(" ")
    if len(token_parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization header.")
    payload = verify_token(token_parts[1])
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    username = payload["sub"]
    caller_id = get_user_by_username(conn, username)
    if caller_id is None:
        raise HTTPException(status_code=401, detail="User not found.")
    return caller_id
