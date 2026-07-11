from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import logging
import re

from app.database import get_db
from app.security import verify_admin_token


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

# Change to "template" if your folder is named template
templates = Jinja2Templates(directory="templates")

FILE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_file_id(file_id: str):
    if not FILE_ID_PATTERN.fullmatch(file_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid file id."
        )


def format_size(size_in_bytes: int) -> str:
    """Convert bytes into readable format."""
    units = ["Bytes", "KB", "MB", "GB", "TB"]

    size = float(size_in_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


# -------------------------------------------------------
# Admin Dashboard
# -------------------------------------------------------

@router.get("/dashboard", response_class=HTMLResponse)
async def get_admin_dashboard(
    request: Request,
    authenticated: bool = Depends(verify_admin_token),
):
    db = get_db()

    try:
        total_files = await db.files.count_documents({})
        total_users = await db.users.count_documents({})

        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_downloads": {
                        "$sum": {
                            "$ifNull": ["$download_count", 0]
                        }
                    },
                    "total_bytes": {
                        "$sum": {
                            "$ifNull": ["$file_size", 0]
                        }
                    },
                }
            }
        ]

        results = await db.files.aggregate(pipeline).to_list(length=1)

        stats = (
            results[0]
            if results
            else {
                "total_downloads": 0,
                "total_bytes": 0,
            }
        )

        recent_files = await (
            db.files.find()
            .sort("uploaded_at", -1)
            .limit(10)
            .to_list(length=10)
        )

        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "total_files": total_files,
                "total_users": total_users,
                "total_downloads": stats.get(
                    "total_downloads",
                    0,
                ),
                "total_storage": format_size(
                    stats.get("total_bytes", 0)
                ),
                "recent_files": recent_files,
            },
        )

    except Exception:
        logger.exception("Failed to load admin dashboard.")

        raise HTTPException(
            status_code=500,
            detail="Unable to load dashboard."
        )


# -------------------------------------------------------
# Delete File
# -------------------------------------------------------

@router.delete("/delete/{file_id}")
async def delete_indexed_file(
    file_id: str,
    authenticated: bool = Depends(verify_admin_token),
):
    validate_file_id(file_id)

    db = get_db()

    try:
        result = await db.files.delete_one(
            {"file_id": file_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )

        logger.info(
            "Admin deleted file %s",
            file_id,
        )

        return {
            "status": "success",
            "message": "File deleted successfully.",
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Unable to delete file."
        )

        raise HTTPException(
            status_code=500,
            detail="Database error."
        )