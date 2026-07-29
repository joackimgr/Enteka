from fastapi import APIRouter, UploadFile, File, Response
from encryption import encrypt_bytes, decrypt_bytes
import os
import uuid

router = APIRouter(tags=["uploads"])

os.makedirs("uploads", exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join("uploads", filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(encrypt_bytes(content))
    return {"image_url": f"/uploads/{filename}"}

@router.get("/uploads/{filename}")
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
