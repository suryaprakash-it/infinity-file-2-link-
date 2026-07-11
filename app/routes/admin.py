from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.security import verify_admin_token # Hooked to Phase 6 Admin token validator

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

def format_size(size_in_bytes: int) -> str:
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

@router.get("/dashboard", response_class=HTMLResponse)
async def get_admin_dashboard(request: Request):
    db = get_db()
    
    # 📊 Aggregations for real-time storage metrics
    total_files = await db.files.count_documents({})
    total_users = await db.users.count_documents({})
    
    # Calculate Total Download Count and Storage Footprint
    pipeline = [
        {"$group": {
            "_id": None, 
            "total_downloads": {"$sum": "$download_count"},
            "total_bytes": {"$sum": "$file_size"}
        }}
    ]
    cursor = db.files.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    
    stats = results[0] if results else {"total_downloads": 0, "total_bytes": 0}
    
    # Fetch recent uploads (Phase 9 feature)
    recent_uploads_cursor = db.files.find().sort("uploaded_at", -1).limit(10)
    recent_uploads = await recent_uploads_cursor.to_list(length=10)

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "total_files": total_files,
        "total_users": total_users,
        "total_downloads": stats.get("total_downloads", 0),
        "total_storage": format_size(stats.get("total_bytes", 0)),
        "recent_files": recent_uploads
    })

@router.delete("/delete/{file_id}")
async def delete_indexed_file(file_id: str, authenticated: bool = Depends(verify_admin_token)):
    db = get_db()
    delete_result = await db.files.delete_one({"file_id": file_id})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File index entry not found.")
        
    return {"status": "success", "message": f"File {file_id} successfully deleted from database index."}
