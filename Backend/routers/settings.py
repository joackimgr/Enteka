from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from db.schemas import UpdateUsername, UpdateEmail, UpdatePassword, UpdateProfilePicture
from db.database import get_user_profile, get_user_hash_by_id, update_username, update_email, update_password, update_profile_picture
from security.auth import create_access_token
from security.encryption import verify, hashing
from core.utils import authenticate_caller
from core import state
import logging

logger = logging.getLogger("enteka.routers.settings")
router = APIRouter(tags=["settings"])

@router.get("/users/me")
async def get_me(authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    profile = get_user_profile(state.conn, caller_id)
    if profile is None:
        return JSONResponse(status_code=404, content={"auth": False, "message": "User not found."})
    return {"auth": True, "profile": profile}

@router.put("/users/me/username")
async def change_username(user_data: UpdateUsername, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    new_username = update_username(state.conn, caller_id, user_data.username)
    if new_username is None:
        return JSONResponse(status_code=409, content={"auth": False, "message": "Username already taken."})
    token = create_access_token(new_username)
    logger.info("User id %s changed username to '%s'.", caller_id, new_username)
    return {"auth": True, "token": token, "username": new_username}

@router.put("/users/me/email")
async def change_email(user_data: UpdateEmail, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    new_email = update_email(state.conn, caller_id, user_data.email)
    if new_email is None:
        return JSONResponse(status_code=409, content={"auth": False, "message": "Email already taken."})
    logger.info("User id %s changed email to '%s'.", caller_id, new_email)
    return {"auth": True, "message": "Email updated."}

@router.put("/users/me/password")
async def change_password(user_data: UpdatePassword, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    stored_hash = get_user_hash_by_id(state.conn, caller_id)
    if stored_hash is None:
        return JSONResponse(status_code=404, content={"auth": False, "message": "User not found."})
    if not verify(user_data.current_password, stored_hash):
        return JSONResponse(status_code=401, content={"auth": False, "message": "Current password is incorrect."})
    new_hash = hashing(user_data.new_password)
    if update_password(state.conn, caller_id, new_hash) is None:
        return JSONResponse(status_code=500, content={"auth": False, "message": "Failed to update password."})
    logger.info("User id %s changed password.", caller_id)
    return {"auth": True, "message": "Password updated."}

@router.put("/users/me/profile-picture")
async def change_profile_picture(user_data: UpdateProfilePicture, authorization: str = Header(None)):
    if state.conn is None:
        raise HTTPException(status_code=503, detail="Database connection error.")
    caller_id = authenticate_caller(state.conn, authorization)
    if not user_data.image_url.startswith("/uploads/"):
        return JSONResponse(status_code=400, content={"auth": False, "message": "Invalid image URL."})
    image_url = update_profile_picture(state.conn, caller_id, user_data.image_url)
    if image_url is None:
        return JSONResponse(status_code=500, content={"auth": False, "message": "Failed to update profile picture."})
    logger.info("User id %s updated profile picture.", caller_id)
    return {"auth": True, "profile_picture": image_url}
