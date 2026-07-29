from fastapi import APIRouter, UploadFile, File, Response, HTTPException
from security.encryption import encrypt_bytes, decrypt_bytes
import os
import uuid
import logging

logger = logging.getLogger("enteka.routers.uploads")
router = APIRouter(tags=["uploads"])

os.makedirs("uploads", exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join("uploads", filename)
    content = await file.read()
    try:
        with open(filepath, "wb") as f:
            f.write(encrypt_bytes(content))
    except OSError as e:
        logger.error("Failed to save upload: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save file.")
    logger.info("Upload saved: %s", filename)
    return {"image_url": f"/uploads/{filename}"}

@router.get("/uploads/{filename}")
async def serve_upload(filename: str):
    filepath = os.path.normpath(os.path.join("uploads", filename))
    if not filepath.startswith("uploads" + os.sep) or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    ext = filename.split(".")[-1].lower()
    media_type = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "webp": "image/webp",
    }.get(ext, "application/octet-stream")
    try:
        with open(filepath, "rb") as f:
            data = decrypt_bytes(f.read())
    except OSError as e:
        logger.error("Failed to read upload: %s", e)
        raise HTTPException(status_code=500, detail="Failed to read file.")
    return Response(content=data, media_type=media_type)