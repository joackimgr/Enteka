from fastapi import APIRouter
from schemas import UserSignUp, UserLogin, TokenRequest
from database import get_user_hash, insert_user
from encryption import hashing, verify
from auth import create_access_token, verify_token
import state

router = APIRouter(tags=["auth"])

@router.post("/signup")
async def signup(user_data: UserSignUp):
    if state.conn is not None:
        hashed_password = get_user_hash(state.conn, user_data.username)
        if hashed_password is None:
            hashing_password = hashing(user_data.password)
            insert_user(state.conn, user_data.username, user_data.email, hashing_password)
            token = create_access_token(user_data.username)
            return {"message": "User created successfully!", "token": token, "auth": True}
        else:
            return {"message": "User already exists.", "auth": False}
    else:
        return {"message": "Error! Cannot establish the database connection."}

@router.post("/login")
async def login(user_data: UserLogin):
    if state.conn is not None:
        stored_hash = get_user_hash(state.conn, user_data.username)
        if stored_hash is None:
            return {"message": "Invalid username or password.", "auth": False}
        if verify(user_data.password, stored_hash):
            token = create_access_token(user_data.username)
            return {"message": "User authenticated successfully!", "token": token, "auth": True}
        else:
            return {"message": "Invalid username or password.", "auth": False}
    else:
        return {"message": "Error! Cannot establish the database connection."}

@router.post("/verify")
async def verify_endpoint(token: TokenRequest):
    result = verify_token(token.token)
    if result:
        return {"auth": True, "username": result["sub"]}
    else:
        return {"auth": False, "message": "Invalid or expired token."}
