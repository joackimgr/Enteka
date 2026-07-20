from fastapi import FastAPI, Header, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import *
from encryption import hashing, verify
from auth import create_access_token, verify_token
from datetime import datetime

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

class CreateChat(BaseModel):
    user2_id: int

class CreateMessage(BaseModel):
    chat_id: int
    content: str

class ConnectionManager():
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket, chat_id):
        await websocket.accept()
        if chat_id not in self.active_connections: self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, websocket, chat_id):
        self.active_connections[chat_id].remove(websocket)
        if not self.active_connections[chat_id]:
            del self.active_connections[chat_id]

    async def broadcast(self, message, chat_id, exclude=None):
        for connection in self.active_connections.get(chat_id, []):
            if connection != exclude:
                await connection.send_json(message)

manager = ConnectionManager()

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Backend is working!"}

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
        return {"message": "Error! Cannot estblish the database connection."}

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
        return {"message": "Error! Cannot estblish the database connection."}

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

@app.post("/chats")
async def chats_post(chat_data: CreateChat, authorization: str = Header(None)):
    if conn is not None:
        if authorization is None:
            return {"message": "Not authenticated.", "auth": False}
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if payload is None:
            return {"message": "Invalid or expired token.", "auth": False}

        username = payload["sub"]
        caller_id = get_user_by_username(conn, username)
        if caller_id is None: 
            return {"message": "User not found."}
        
        result = create_chat(conn, caller_id, chat_data.user2_id)
        return {"auth": True, "chat": result}
    else:
        return {"message": "Error! Cannot estblish the database connection."}
    

@app.get("/chats")
async def chats_get(authorization: str = Header(None)):
    if conn is not None:
        if authorization is None:
            return {"message": "Not authenticated.", "auth": False}
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if payload is None:
            return {"message": "Invalid or expired token.", "auth": False}
        
        username = payload["sub"]
        caller_id = get_user_by_username(conn, username)
        if caller_id is None: 
            return {"message": "Failed to get chat."}
        
        chat_list = get_chats_by_user_id(conn, caller_id)
        if chat_list is None:
            return {"auth": False, "chats": [], "message": "Failed to get chats."}

        formatted_chats = []
        for row in chat_list:
            if row[1] == caller_id:
                other_user_id = row[2]
            else:
                other_user_id = row[1]
            other_username = get_user_by_id(conn, other_user_id)
            last_msg = get_last_message_by_chat_id(conn, row[0])
            if last_msg:
                formatted_chats.append({
                    "chat_id": row[0],
                    "other_username": other_username,
                    "passkey_hash": row[3],
                    "created_at": row[4],
                    "last_message": last_msg[0] if last_msg else None,
                    "last_timestamp": last_msg[1].split()[1][:5] if last_msg else None
                })
        return {"auth": True, "chats": formatted_chats}
    else:
        return {"message": "Error! Cannot estblish the database connection."}


@app.post("/messages")
async def messages_post(message_data: CreateMessage, authorization: str = Header(None)):
    if conn is not None:
        if authorization is None:
            return {"message": "Not authenticated.", "auth": False}
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if payload is None:
            return {"message": "Invalid or expired token.", "auth": False}
        
        username = payload["sub"]
        sender_id = get_user_by_username(conn, username)
        if sender_id is None: 
            return {"message": "User not found."}
        
        result = insert_message(conn, message_data.chat_id, sender_id, message_data.content)
        return {"auth": True, "message_id": result}
    else:
        return {"message": "Error! Cannot estblish the database connection."}

@app.get("/messages/{chat_id}")
async def messages_get(chat_id: int, authorization: str = Header(None)):
    if conn is not None:
        if authorization is None:
            return {"message": "Not authenticated.", "auth": False}
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if payload is None:
            return {"message": "Invalid or expired token.", "auth": False}
        username = payload["sub"]
        caller_id = get_user_by_username(conn, username)
        if caller_id is None:
            return {"message": "User doesn't exist", "auth": False}
        chat_list = get_messages_by_chat_id(conn, chat_id)
        messages = [{"id": msg[0], "sender_id": msg[1], "content": msg[2], "timestamp": msg[3].split()[1][:5], "is_mine": msg[1] == caller_id} for msg in chat_list]
        return {"auth": True, "messages": messages}
    else:
        return {"message": "Error! Cannot estblish the database connection."}

@app.get("/users/suggestions")
async def user_suggestions(authorization: str = Header(None)):
    if conn is not None:
        if authorization is None:
            return {"message": "Not authenticated.", "auth": False}
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if payload is None:
            return {"message": "Invalid or expired token.", "auth": False}
        username = payload["sub"]
        caller_id = get_user_by_username(conn, username)
        if caller_id is None:
            return {"message": "User doesn't exist", "auth": False}
        user_suggest =  get_user_suggestions(conn, caller_id)
        return {"auth": True, "suggestions": user_suggest}
    else: 
        return {"message": "Error! Cannot establish the database connection."}
    
@app.websocket("/ws/{chat_id}")
async def webSocket_endpoint(websocket: WebSocket, chat_id: int, token: str = Query()):
    if conn is not None:
        payload = verify_token(token)
        if payload is None:
            await websocket.close(code=1008)
            return None
        username = payload["sub"]
        caller_id = get_user_by_username(conn, username)
        if caller_id is None:
            await websocket.close(code=1008)
            return
        
        await manager.connect(websocket, chat_id)
        try: 
            while True: 
                data = await websocket.receive_json()
                msg_type = data.get("type", "message")
                if msg_type == "message":
                    content = data["content"]
                    message_id = insert_message(conn, chat_id, caller_id, content)
                    await manager.broadcast({"type": "new_message",
                                            "message_id": message_id,
                                            "caller_id": caller_id,
                                            "username": username,
                                            "content": content,
                                            "timestamp": datetime.now().strftime("%H:%M")
                                            }, chat_id)
                elif msg_type == "typing":
                    await manager.broadcast({"type": "typing", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "stop_typing":
                    await manager.broadcast({"type": "stop_typing", "username": username}, chat_id, exclude=websocket)
        except WebSocketDisconnect: manager.disconnect(websocket, chat_id)