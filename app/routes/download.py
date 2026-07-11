from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
import logging

from app.database import get_db
from bot.bot import app_bot

def validate_file_id(file_id: str):
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if not file_id or any(ch not in allowed for ch in file_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid file id."
        )


logger = logging.getLogger(__name__)
router = APIRouter()

templates = Jinja2Templates(directory="templates")

def format_size(size_in_bytes: int) -> str:
    """Helper to convert sizes cleanly into human-readable parameters"""
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

# --- 🎨 FRONTEND FILE INFORMATION ROUTE ---
@router.get("/download/{file_id}")
async def get_file_info_page(file_id: str, request: Request):
    db = get_db()
    file_doc = await db.files.find_one({"file_id": file_id})
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="Requested file mapping is invalid or expired.")
        
    return templates.TemplateResponse("download.html", {
        "request": request,
        "file": file_doc,
        "file_size_formatted": format_size(file_doc["file_size"]),
        "current_url": str(request.url)
    })

# --- 📥 ENGINE STREAMING BACKEND ROUTE ---
@router.get("/api/download/{file_id}")
async def stream_telegram_file(file_id: str, request: Request):
    db = get_db()
    file_doc = await db.files.find_one({"file_id": file_id})
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="File records not found.")

    await db.files.update_one({"file_id": file_id}, {"$inc": {"download_count": 1}})

    try:
        message = await app_bot.get_messages(chat_id=file_doc["chat_id"], message_ids=file_doc["message_id"])
    except Exception as e:
        logger.error(f"Error reading MTProto message structure: {e}")
        raise HTTPException(status_code=500, detail="Error fetching file from Telegram cloud.")

    async def file_stream_generator():
        async for chunk in app_bot.stream_media(message):
            if await request.is_disconnected():
                break
            yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename="{file_doc["file_name"]}"',
        "Content-Length": str(file_doc["file_size"]),
        "Accept-Ranges": "bytes"
    }
    
    return StreamingResponse(file_stream_generator(), media_type=file_doc["mime_type"], headers=headers)
