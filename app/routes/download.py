from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

import logging
import re
from urllib.parse import quote

from app.database import get_db
from bot.bot import app_bot


logger = logging.getLogger(__name__)

router = APIRouter()

# Change to "template" if your folder is named template
templates = Jinja2Templates(directory="templates")

# Allow only valid Telegram file IDs
FILE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_file_id(file_id: str):
    if not FILE_ID_PATTERN.fullmatch(file_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid file id."
        )


def format_size(size_in_bytes: int) -> str:
    """Convert bytes into a human readable string."""
    units = ["Bytes", "KB", "MB", "GB", "TB"]

    size = float(size_in_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


# -------------------------------------------------------
# Frontend Download Page
# -------------------------------------------------------

@router.get("/download/{file_id}")
async def get_file_info_page(file_id: str, request: Request):

    validate_file_id(file_id)

    db = get_db()

    file_doc = await db.files.find_one({"file_id": file_id})

    if file_doc is None:
        raise HTTPException(
            status_code=404,
            detail="Requested file not found."
        )

    return templates.TemplateResponse(
        "download.html",
        {
            "request": request,
            "file": file_doc,
            "file_size_formatted": format_size(
                file_doc.get("file_size", 0)
            ),
            "current_url": str(request.url),
        },
    )


# -------------------------------------------------------
# Telegram Streaming Endpoint
# -------------------------------------------------------

@router.get("/api/download/{file_id}")
async def stream_telegram_file(file_id: str, request: Request):

    validate_file_id(file_id)

    db = get_db()

    file_doc = await db.files.find_one({"file_id": file_id})

    if file_doc is None:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    # Update download counter
    try:
        await db.files.update_one(
            {"file_id": file_id},
            {"$inc": {"download_count": 1}},
        )
    except Exception as e:
        logger.warning(f"Unable to update download count: {e}")

    # Fetch Telegram message
    try:
        message = await app_bot.get_messages(
            chat_id=file_doc["chat_id"],
            message_ids=file_doc["message_id"],
        )

    except Exception:
        logger.exception("Failed to fetch Telegram message.")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch file from Telegram."
        )

    async def file_stream():

        try:

            async for chunk in app_bot.stream_media(message):

                if await request.is_disconnected():
                    logger.info("Client disconnected.")
                    break

                yield chunk

        except Exception:
            logger.exception("Streaming failed.")
            raise

    filename = quote(file_doc.get("file_name", "download"))

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
        "Content-Length": str(file_doc.get("file_size", 0)),
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-cache",
    }

    return StreamingResponse(
        file_stream(),
        media_type=file_doc.get(
            "mime_type",
            "application/octet-stream",
        ),
        headers=headers,
    )