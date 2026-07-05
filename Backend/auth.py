import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
token_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(username):
    exp = (datetime.now(timezone.utc) + timedelta(minutes=token_expire)).timestamp()
    encoded = jwt.encode({"sub":username, "exp":exp}, key, algorithm)
    return encoded

def verify_token(token):
    try:
        decoded = jwt.decode(token, key, algorithms=[algorithm])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
