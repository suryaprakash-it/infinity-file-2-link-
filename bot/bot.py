import logging

from pyrogram import Client, filters
from pyrogram.errors import RPCError
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
    in_memory=True,
)


def generate_link(file_id: str) -> str:
    return f"{settings.SERVER_URL}/download/{file_id}"


# ---------------------------------------------------
# Start Command
# ---------------------------------------------------

@app_bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):

    db = get_db()

    if db and message.from_user:

        try:

            await db.users.update_one(
                {"user_id": message.from_user.id},
                {
                    "$set": {
                        "user_id": message.from_user.id,
                        "username": message.from_user.username,
                        "first_name": message.from_user.first_name,
                    }
                },
                upsert=True,
            )

        except Exception:
            logger.exception("Unable to save user.")

    await message.reply_text(
        "👋 **Welcome to Infinity Share!**\n\n"
        "📤 Send me any file.\n"
        "🔗 I'll generate a permanent download link."
    )


# ---------------------------------------------------
# Media Upload
# ---------------------------------------------------

@app_bot.on_message(filters.media & filters.private)
async def media_handler(client: Client, message: Message):

    db = get_db()

    media = getattr(message, message.media.value)

    file_id = media.file_id

    link = generate_link(file_id)

    try:

        existing = await db.files.find_one(
            {"file_id": file_id}
        )

        if existing:

            await message.reply_text(
                f"✅ **Already Indexed!**\n\n🔗 `{link}`"
            )

            return

        file_data = FileModel(
            file_id=file_id,
            message_id=message.id,
            chat_id=message.chat.id,
            file_name=getattr(
                media,
                "file_name",
                f"File_{message.id}",
            ),
            file_size=getattr(
                media,
                "file_size",
                0,
            ),
            mime_type=getattr(
                media,
                "mime_type",
                None,
            )
            or "application/octet-stream",
        )

        await db.files.insert_one(
            file_data.model_dump()
        )

        logger.info(
            "Indexed %s",
            file_data.file_name,
        )

        await message.reply_text(
            f"✅ **Link Generated Successfully!**\n\n"
            f"🔗 `{link}`"
        )

    except RPCError:
        logger.exception("Telegram API error.")

        await message.reply_text(
            "❌ Telegram error occurred."
        )

    except Exception:
        logger.exception("Unexpected error.")

        await message.reply_text(
            "❌ Internal server error."
        )