from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import create_table, create_connection, insert_user, get_user_hash
from encryption import hashing, verify


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
            return {"message": "User created successfully!", "auth": True}
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
            return {"message": "User authenticated successfully!", "auth": True}
        else:
            return {"message": "Invalid username or password.", "auth": False}
    else:
        return {"message": "Error! Cannot create the database connection."}
