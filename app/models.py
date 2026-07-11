from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FileModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )

    file_id: str = Field(
        ...,
        min_length=1,
        description="Unique Telegram file ID",
    )

    message_id: int = Field(
        ...,
        ge=1,
        description="Telegram message ID",
    )

    chat_id: int = Field(
        ...,
        description="Telegram chat ID",
    )

    file_name: str = Field(
        ...,
        min_length=1,
    )

    file_size: int = Field(
        ...,
        ge=0,
        description="File size in bytes",
    )

    mime_type: str = Field(
        default="application/octet-stream",
    )

    custom_alias: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    download_count: int = Field(
        default=0,
        ge=0,
    )

    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow,
    )


class UserModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )

    user_id: int = Field(
        ...,
        ge=1,
    )

    username: Optional[str] = Field(
        default=None,
        max_length=64,
    )

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )

    joined_at: datetime = Field(
        default_factory=datetime.utcnow,
    )