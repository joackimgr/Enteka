import os
import sys
import tempfile

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["MAX_UPLOAD_SIZE_MB"] = "5"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-not-for-production"

import pytest
from fastapi.testclient import TestClient
from db.database import create_connection, create_table
from core.connection_manager import ConnectionManager
from core import state
from routers import auth, chats, friends, uploads, ws, settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@pytest.fixture()
def app(tmp_path):
    db_path = os.path.join(str(tmp_path), "test.db")
    upload_dir = os.path.join(str(tmp_path), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    os.environ["UPLOAD_DIR"] = upload_dir
    uploads.UPLOAD_DIR = upload_dir
    conn = create_connection(db_path)
    create_table(conn)
    state.conn = conn
    state.manager = ConnectionManager()

    app = FastAPI()
    app.add_middleware(CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(auth.router)
    app.include_router(chats.router)
    app.include_router(friends.router)
    app.include_router(uploads.router)
    app.include_router(ws.router)
    app.include_router(settings.router)

    @app.get("/")
    async def root():
        return {"message": "Backend is working!"}

    with TestClient(app) as client:
        yield client

    conn.close()
    state.conn = None
    state.manager = None


@pytest.fixture()
def signup(app):
    counter = {"n": 0}

    def _signup(username=None):
        counter["n"] += 1
        uname = username or f"user{counter['n']}"
        resp = app.post("/signup", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "password123",
        })
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["auth"] is True
        return {"username": uname, "email": f"{uname}@test.com", "password": "password123", "token": data["token"]}

    return _signup


@pytest.fixture()
def auth_headers():
    def _headers(token):
        return {"Authorization": f"Bearer {token}"}

    return _headers
