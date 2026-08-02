from fastapi import APIRouter, UploadFile, File, Response, HTTPException, Header, Query
from security.encryption import encrypt_bytes, decrypt_bytes
from core.utils import authenticate_caller
from core import state
import os
import uuid
import logging

logger = logging.getLogger("enteka.routers.uploads")
router = APIRouter(tags=["uploads"])

os.makedirs("uploads", exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5")) * 1024 * 1024
MEDIA_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "webp": "image/webp", "gif": "image/gif"
    }

def valid_image(data):
    if data[:3] == b"\xff\xd8\xff": return True
    if data[:8] == b"\x89PNG\r\n\x1a\n": return True
    if data[:6] in (b"GIF87a", b"GIF89a"): return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return True
    return False

@router.post("/upload")
async def upload_image(authorization: str = Header(None), file: UploadFile = File(...)):
    authenticate_caller(state.conn, authorization)
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name.")
    
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    chunks = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        chunks.append(chunk)

    content = b"".join(chunks)
    if not content:
        raise HTTPException(status_code=400, detail="File is empty.")
    if not valid_image(content):
        raise HTTPException(status_code=400, detail="File is not a valid image.")
    
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join("uploads", filename)
    try:
        with open(filepath, "wb") as f:
            f.write(encrypt_bytes(content))
    except OSError as e:
        logger.error("Failed to save upload: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save file.")
    logger.info("Upload saved: %s", filename)
    return {"image_url": f"/uploads/{filename}"}

@router.get("/uploads/{filename}")
async def serve_upload(filename: str, token: str = Query(None)):
    authenticate_caller(state.conn, f"Bearer {token}" if token else None)

    filepath = os.path.normpath(os.path.join("uploads", filename))
    if not filepath.startswith("uploads" + os.sep) or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=404, detail="File not found")    
    try:
        with open(filepath, "rb") as f:
            data = decrypt_bytes(f.read())
    except OSError as e:
        logger.error("Failed to read upload: %s", e)
        raise HTTPException(status_code=500, detail="Failed to read file.")
    return Response(content=data, media_type=MEDIA_TYPES.get(ext, "application/octet-stream"))