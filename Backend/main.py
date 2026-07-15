from fastapi import FastAPI, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import *
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

class CreateChat(BaseModel):
    user2_id: int

class CreateMessage(BaseModel):
    chat_id: int
    content: str

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
        return {"message": "Error! Cannot create the database connection."}
    

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
            return {"auth": False, "chats": [], "message": "Failed to get message."}

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
        return {"message": "Error! Cannot create the database connection."}


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
        return {"message": "Error! Cannot create the database connection."}

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
        return {"message": "Error! Cannot create the database connection."}
