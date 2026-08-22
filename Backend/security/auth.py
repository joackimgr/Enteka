from fastapi import HTTPException, status
import jwt
import os
from typing import Any
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

key: str | None = os.getenv("SECRET_KEY")
algorithm: str | None = os.getenv("ALGORITHM")
token_expire: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not key:
    raise RuntimeError("SECRET_KEY environment variable is missing!")

def create_access_token(username: str) -> str:
    exp = (datetime.now(timezone.utc) + timedelta(minutes=token_expire)).timestamp()
    token = jwt.encode({"sub":username, "exp":exp}, key, algorithm)
    return token

def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, key, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
