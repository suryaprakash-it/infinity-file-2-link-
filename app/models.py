from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FileModel(BaseModel):
    file_id: str = Field(..., description="Unique Telegram file_id")
    message_id: int = Field(..., description="Telegram message ID for streaming reference")
    chat_id: int = Field(..., description="Chat ID where the file resides")
    file_name: str
    file_size: int
    mime_type: str = "application/octet-stream"
    custom_alias: Optional[str] = None
    download_count: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class UserModel(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)
