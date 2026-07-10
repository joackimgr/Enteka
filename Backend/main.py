from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import create_table, create_connection, insert_user, get_user_hash, search_users
from encryption import hashing, verify
from auth import create_access_token, verify_token


conn = create_connection("Enteka.db")
create_table(conn)

app = FastAPI()

class UserSignUp(BaseModel):
    username: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class TokenRequest(BaseModel):
    token: str

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Python backend is working!"}

@app.post("/signup")
async def signup(user_data: UserSignUp):
    if conn is not None:
        hashed_password = get_user_hash(conn, user_data.username)

        if hashed_password is None:
            hashing_password = hashing(user_data.password)
            insert_user(conn, user_data.username, user_data.email, hashing_password)
            token = create_access_token(user_data.username)
            return {"message": "User created successfully!","token": token, "auth": True}
        else:
            return {"message": "User already exists.", "auth": False}
    else:
        return {"message": "Error! Cannot create the database connection."}

@app.post("/login")
async def login(user_data: UserLogin):
    if conn is not None:
        stored_hash = get_user_hash(conn, user_data.username)
        if stored_hash is None:
            return {"message": "Invalid username or password.", "auth": False}
        if verify(user_data.password, stored_hash):
            token = create_access_token(user_data.username)
            return {"message": "User authenticated successfully!","token": token, "auth": True}
        else:
            return {"message": "Invalid username or password.", "auth": False}
    else:
        return {"message": "Error! Cannot create the database connection."}

@app.post("/verify")
async def verify_endpoint(token: TokenRequest):
    result = verify_token(token.token)
    if result:
        return {"auth": True, "username": result["sub"]}
    else:
        return {"auth": False, "message": "Invalid or expired token."}
    
@app.get("/users/search")
async def search(query: str = ""):
    result = search_users(conn, query)
    return result