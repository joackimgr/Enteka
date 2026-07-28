import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

encryption_key = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(encryption_key) if encryption_key else None

def hashing(password):
    byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashing = bcrypt.hashpw(byte, salt)
    return hashing.decode('utf-8')

def verify(password, stored_hash):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def encrypt(text):
    if cipher is None:
        return text
    return cipher.encrypt(text.encode()).decode()

def decrypt(token):
    if cipher is None:
        return token
    return cipher.decrypt(token.encode()).decode()

def encrypt_bytes(data):
    if cipher is None:
        return data
    return cipher.encrypt(data)

def decrypt_bytes(data):
    if cipher is None:
        return data
    return cipher.decrypt(data)