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

class UpdateUsername(BaseModel):
    username: str

class UpdateEmail(BaseModel):
    email: EmailStr

class UpdatePassword(BaseModel):
    current_password: str
    new_password: str

class UpdateProfilePicture(BaseModel):
    image_url: str