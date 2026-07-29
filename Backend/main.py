from fastapi import FastAPI, Header, WebSocket, WebSocketDisconnect, Query, UploadFile, File, Response
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from database import *
from encryption import hashing, verify, encrypt_bytes, decrypt_bytes
from auth import create_access_token, verify_token
from datetime import datetime
import os
import uuid

conn = create_connection("Enteka.db")
create_table(conn)

app = FastAPI()

class UserSignUp(BaseModel):
    username: str
    email: EmailStr
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

p_ip = os.getenv("P_IP", "localhost")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", f"http://{p_ip}:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

def authenticate_caller(conn, authorization):
    if authorization is None:
        return None, {"message": "Not authenticated.", "auth": False}
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload is None:
        return None, {"message": "Invalid or expired token.", "auth": False}
    username = payload["sub"]
    caller_id = get_user_by_username(conn, username)
    if caller_id is None: 
        return None, {"message": "User not found."}
    return caller_id, None

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
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        result = create_chat(conn, caller_id, chat_data.user2_id)
        return {"auth": True, "chat": result}
    else:
        return {"message": "Error! Cannot estblish the database connection."}
    

@app.get("/chats")
async def chats_get(authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
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
                    "last_image": last_msg[1] if last_msg else None,
                    "last_timestamp": last_msg[2].split()[1][:5] if last_msg else None
                })
        return {"auth": True, "chats": formatted_chats}
    else:
        return {"message": "Error! Cannot estblish the database connection."}


@app.post("/messages")
async def messages_post(message_data: CreateMessage, authorization: str = Header(None)):
    if conn is not None:
        sender_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        result = insert_message(conn, message_data.chat_id, sender_id, message_data.content)
        return {"auth": True, "message_id": result}
    else:
        return {"message": "Error! Cannot estblish the database connection."}

@app.get("/messages/{chat_id}")
async def messages_get(chat_id: int, authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        chat_list = get_messages_by_chat_id(conn, chat_id)
        if chat_list is None:
            return {"auth": True, "messages": []}
        messages = [{"id": msg[0], "sender_id": msg[1], "content": msg[2], "image": msg[3], "timestamp": msg[4].split()[1][:5], "is_mine": msg[1] == caller_id} for msg in chat_list]
        return {"auth": True, "messages": messages}
    else:
        return {"message": "Error! Cannot estblish the database connection."}

@app.get("/users/suggestions")
async def user_suggestions(authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        user_suggest =  get_user_suggestions(conn, caller_id)
        return {"auth": True, "suggestions": user_suggest}
    else: 
        return {"message": "Error! Cannot establish the database connection."}
    
os.makedirs("uploads", exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join("uploads", filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(encrypt_bytes(content))
    return {"image_url": f"/uploads/{filename}"}

@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    filepath = os.path.normpath(os.path.join("uploads", filename))
    if not filepath.startswith("uploads" + os.sep) or not os.path.exists(filepath):
        return Response(status_code=404)
    ext = filename.split(".")[-1].lower()
    media_type = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "webp": "image/webp",
    }.get(ext, "application/octet-stream")
    with open(filepath, "rb") as f:
        data = decrypt_bytes(f.read())
    return Response(content=data, media_type=media_type)

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
                                            "image_url": None,
                                            "timestamp": datetime.now().strftime("%H:%M")
                                            }, chat_id)
                elif msg_type == "image":
                    content = data.get("content", "")
                    image_url = data["image_url"]
                    message_id = insert_message(conn, chat_id, caller_id, content, image_url)
                    await manager.broadcast({"type": "new_message",
                                            "message_id": message_id,
                                            "caller_id": caller_id,
                                            "username": username,
                                            "content": content,
                                            "image_url": image_url,
                                            "timestamp": datetime.now().strftime("%H:%M")
                                            }, chat_id)
                elif msg_type == "typing":
                    await manager.broadcast({"type": "typing", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "stop_typing":
                    await manager.broadcast({"type": "stop_typing", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "call_offer":
                    await manager.broadcast({"type": "call_offer", "username": username, "data": data.get("data")}, chat_id, exclude=websocket)
                elif msg_type == "call_answer":
                    await manager.broadcast({"type": "call_answer", "username": username, "data": data.get("data")}, chat_id, exclude=websocket)
                elif msg_type == "ice_candidate":
                    await manager.broadcast({"type": "ice_candidate", "username": username, "data": data.get("data")}, chat_id, exclude=websocket)
                elif msg_type == "call_end":
                    await manager.broadcast({"type": "call_end", "username": username}, chat_id, exclude=websocket)
                elif msg_type == "call_reject":
                    await manager.broadcast({"type": "call_reject", "username": username}, chat_id, exclude=websocket)
        except WebSocketDisconnect: manager.disconnect(websocket, chat_id)

@app.post("/friends/request/{user_id}")
async def request_friends(user_id: int, authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        result = send_friend_request(conn, caller_id, user_id)
        if result:
            return {"auth": True, "message": "Friend request sent."}
        return {"auth": False, "message": "Friend request already sent."}
    return {"message": "Error! Cannot establish the database connection."}

@app.get("/friends/requests")
async def get_request_friends(authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        requests = get_pending_requests(conn, caller_id)
        return {"auth": True, "requests": requests}
    return {"message": "Error! Cannot establish the database connection."}

@app.post("/friends/accept/{request_id}")
async def accept_friends(request_id: int, authorization: str = Header(None)):
    if conn is not None:
        _, error = authenticate_caller(conn, authorization)
        if error:
            return error
        result = accept_friend_request(conn, request_id)
        if result:
            return {"auth": True, "message": "Friend request accepted."}
        return {"auth": False, "message": "Friend request not found."}
    return {"message": "Error! Cannot establish the database connection."}

@app.post("/friends/reject/{request_id}")
async def reject_friends(request_id: int, authorization: str = Header(None)):
    if conn is not None:
        _, error = authenticate_caller(conn, authorization)
        if error:
            return error
        result = reject_friend_request(conn, request_id)
        if result:
            return {"auth": True, "message": "Friend request rejected."}
        return {"auth": False, "message": "Friend request not found."}
    return {"message": "Error! Cannot establish the database connection."}

@app.get("/friends")
async def get_friends_list(authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        friends = get_friends(conn, caller_id)
        return {"auth": True, "friends": friends}
    return {"message": "Error! Cannot establish the database connection."}

@app.delete("/friends/{friend_id}")
async def remove_friends(friend_id: int, authorization: str = Header(None)):
    if conn is not None:
        caller_id, error = authenticate_caller(conn, authorization)
        if error:
            return error
        result = remove_friend(conn, caller_id, friend_id)
        if result:
            return {"auth": True, "message": "Friend removed."}
        return {"auth": False, "message": "Friend not found."}
    return {"message": "Error! Cannot establish the database connection."}