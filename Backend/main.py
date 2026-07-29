import setup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import create_connection, create_table
from core.connection_manager import ConnectionManager
from routers import auth, chats, friends, uploads, ws
from core import state
import os

state.conn = create_connection("Enteka.db")
create_table(state.conn)
state.manager = ConnectionManager()

app = FastAPI()

p_ip = os.getenv("P_IP", "localhost")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", f"http://{p_ip}:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(friends.router)
app.include_router(uploads.router)
app.include_router(ws.router)

@app.get("/")
async def read_root():
    return {"message": "Backend is working!"}