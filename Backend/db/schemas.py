from pydantic import BaseModel, EmailStr

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