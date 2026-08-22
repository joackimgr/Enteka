import os
import bcrypt
import logging
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

load_dotenv()

encryption_key = os.getenv("ENCRYPTION_KEY")
cipher = None

if not encryption_key:
    logger.warning("ENCRYPTION_KEY is not set. Encryption operations will fail.")
else:
    try:
        cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    except Exception as exc:
        logger.error(f"Failed to initialize Fernet with provided key: {exc}")
        cipher = None

def hashing(password: str) -> str:
    byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashing = bcrypt.hashpw(byte, salt)
    return hashing.decode('utf-8')

def verify(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def encrypt(text: str) -> str:
    if cipher is None:
        raise RuntimeError("Cannot encrypt data: Encryption cipher is not initialized.")
    return cipher.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt(token: str) -> str:
    if cipher is None:
        raise RuntimeError("Cannot decrypt data: Encryption cipher is not initialized.")
    try:
        return cipher.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        logger.error("Decryption failed: Invalid token or wrong encryption key.")
        raise ValueError("Failed to decrypt data: Invalid or corrupted token.")

def encrypt_bytes(data: bytes) -> bytes:
    if cipher is None:
        raise RuntimeError("Cannot encrypt data: Encryption cipher is not initialized.")
    return cipher.encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    if cipher is None:
        raise RuntimeError("Cannot decrypt data: Encryption cipher is not initialized.")
    try:
        return cipher.decrypt(data)
    except InvalidToken:
        logger.error("Decryption failed: Invalid token or wrong encryption key.")
        raise ValueError("Failed to decrypt data: Invalid or corrupted token.")
