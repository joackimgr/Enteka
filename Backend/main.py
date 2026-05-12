from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import create_table, create_connection, insert_user, user_exists


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

"""
CORSMiddleware(
    app,
    allow_origins=("http://localhost:5173", "http://localhost:8000"),
    allow_methods=("GET", "POST", "PUT", "DELETE", "OPTIONS"),
    allow_headers=["*"],
    allow_credentials=False,
    allow_origin_regex=None,
    allow_private_network=True,
    expose_headers=[],
    max_age=600,
    access_control_allow_origin="*",
)
"""

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
        if not user_exists(conn, user_data.username, user_data.password):
            insert_user(conn, user_data.username, user_data.email, user_data.password)
            return {"message": "User created successfully!", "auth": True}
        else:
            return {"message": "User already exists.", "auth": False}
    else:
        return {"message": "Error! Cannot create the database connection."}

@app.post("/login")
async def login(user_data: UserLogin):
    if conn is not None:
        if user_exists(conn, user_data.username, user_data.password):
            return {"message": "User authenticated successfully!", "auth": True}
        else:
            return {"message": "Invalid username or password.", "auth": False}
    else:
        return {"message": "Error! Cannot create the database connection."}
