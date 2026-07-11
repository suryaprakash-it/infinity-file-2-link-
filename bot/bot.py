import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from app.config import settings
from app.database import get_db
from app.models import FileModel

logger = logging.getLogger(__name__)

app_bot = Client(
    "infinity_share_bot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN,
    in_memory=True 
)

@app_bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    db = get_db()
    if db is not None:
        user_data = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name
        }
        await db.users.update_one({"user_id": message.from_user.id}, {"$set": user_data}, upsert=True)
        
    await message.reply_text("👋 **Welcome!** Send me any file, and I will generate a permanent download link.")

@app_bot.on_message(filters.media & filters.private)
async def media_handler(client: Client, message: Message):
    media = getattr(message, message.media.value)
    file_id = media.file_id
    db = get_db()
    
    if db is not None:
        existing_file = await db.files.find_one({"file_id": file_id})
        if existing_file:
            link = f"{settings.SERVER_URL}/download/{file_id}"
            await message.reply_text(f"✅ **File Already Indexed!**\n\n🔗 `{link}`")
            return

        new_file = FileModel(
            file_id=file_id,
            message_id=message.id,
            chat_id=message.chat.id,
            file_name=getattr(media, "file_name", f"File_{message.id}"),
            file_size=media.file_size,
            mime_type=media.mime_type or "application/octet-stream"
        )
        await db.files.insert_one(new_file.model_dump())
        
    link = f"{settings.SERVER_URL}/download/{file_id}"
    await message.reply_text(f"✅ **Link Generated!**\n\n🔗 `{link}`")