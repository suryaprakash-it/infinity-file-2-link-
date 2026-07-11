# app/routes/download.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import logging

from app.database import get_db
from bot.bot import app_bot  # Import the active Pyrogram client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/download/{file_id}")
async def stream_telegram_file(file_id: str, request: Request):
    db = get_db()
    
    # 1. Fetch file metadata from MongoDB
    file_doc = await db.files.find_one({"file_id": file_id})
    
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found or expired.")

    # 2. Update Storage Statistics: Increment download count asynchronously
    await db.files.update_one({"file_id": file_id}, {"$inc": {"download_count": 1}})

    # 3. Fetch the message containing the media from Telegram
    try:
        message = await app_bot.get_messages(
            chat_id=file_doc["chat_id"], 
            message_ids=file_doc["message_id"]
        )
    except Exception as e:
        logger.error(f"Failed to fetch message from Telegram: {e}")
        raise HTTPException(status_code=500, detail="Error fetching file from Telegram servers.")

    if not message or not message.media:
        raise HTTPException(status_code=404, detail="Media not accessible in Telegram.")

    # 4. Generator function to yield chunks from Pyrogram directly to the client
    async def file_stream_generator():
        async for chunk in app_bot.stream_media(message):
            # If the client disconnects mid-download, this stops streaming
            if await request.is_disconnected():
                logger.info(f"Client disconnected during download of {file_doc['file_name']}")
                break
            yield chunk

    # 5. Set appropriate headers so the browser triggers a file download
    headers = {
        "Content-Disposition": f'attachment; filename="{file_doc["file_name"]}"',
        "Content-Length": str(file_doc["file_size"]),
        "Accept-Ranges": "bytes"
    }
    
    return StreamingResponse(
        file_stream_generator(), 
        media_type=file_doc["mime_type"], 
        headers=headers
    )
