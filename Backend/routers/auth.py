from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from db.schemas import UserSignUp, UserLogin, TokenRequest
from db.database import get_user_hash, insert_user
from security.encryption import hashing, verify
from security.auth import create_access_token, verify_token
from core import state
import logging

logger = logging.getLogger("enteka.routers.auth")
router = APIRouter(tags=["auth"])

@router.post("/signup")
async def signup(user_data: UserSignUp):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    hashed_password = get_user_hash(state.conn, user_data.username)
    if hashed_password is not None:
        return JSONResponse(status_code=409, content={"auth": False, "message": "User already exists."})
    hashing_password = hashing(user_data.password)
    user_id = insert_user(state.conn, user_data.username, user_data.email, hashing_password)
    if user_id is None:
        return JSONResponse(status_code=409, content={"auth": False, "message": "User already exists."})
    token = create_access_token(user_data.username)
    logger.info("User '%s' signed up.", user_data.username)
    return {"auth": True, "token": token, "message": "User created successfully!"}

@router.post("/login")
async def login(user_data: UserLogin):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    stored_hash = get_user_hash(state.conn, user_data.username)
    if stored_hash is None:
        return JSONResponse(status_code=401, content={"auth": False, "message": "Invalid username or password."})
    if not verify(user_data.password, stored_hash):
        return JSONResponse(status_code=401, content={"auth": False, "message": "Invalid username or password."})
    token = create_access_token(user_data.username)
    logger.info("User '%s' logged in.", user_data.username)
    return {"auth": True, "token": token, "message": "User authenticated successfully!"}

@router.post("/verify")
async def verify_endpoint(token: TokenRequest):
    result = verify_token(token.token)
    if not result:
        return JSONResponse(status_code=401, content={"auth": False, "message": "Invalid or expired token."})
    return {"auth": True, "username": result["sub"]}