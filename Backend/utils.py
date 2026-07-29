from auth import verify_token
from database import get_user_by_username

def authenticate_caller(conn, authorization):
    if authorization is None:
        return None, {"message": "Not authenticated.", "auth": False}
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload is None:
        return None, {"message": "Invalid or expired token.", "auth": False}
    username = payload["sub"]
    caller_id = get_user_by_username(conn, username)
    if caller_id is None:
        return None, {"message": "User not found."}
    return caller_id, None
