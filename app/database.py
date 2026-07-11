from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from app.config import settings

import logging

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient | None = None
    db = None


db_instance = Database()


async def connect_to_mongo():
    """Connect to MongoDB and create required indexes."""

    try:
        logger.info("Connecting to MongoDB...")

        db_instance.client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=10000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            retryWrites=True,
            retryReads=True,
        )

        # Verify connection
        await db_instance.client.admin.command("ping")

        db_name = (
            settings.MONGO_URI.rsplit("/", 1)[-1]
            .split("?")[0]
            or "infinity_share"
        )

        db_instance.db = db_instance.client[db_name]

        # Files Collection
        await db_instance.db.files.create_index(
            "file_id",
            unique=True,
            background=True,
        )

        await db_instance.db.files.create_index(
            "custom_alias",
            unique=True,
            sparse=True,
            background=True,
        )

        await db_instance.db.files.create_index(
            "uploaded_at",
            background=True,
        )

        # Users Collection
        await db_instance.db.users.create_index(
            "user_id",
            unique=True,
            background=True,
        )

        logger.info("MongoDB connected successfully.")

    except PyMongoError:
        logger.exception("Failed to connect to MongoDB.")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""

    if db_instance.client is not None:
        logger.info("Closing MongoDB connection...")
        db_instance.client.close()
        logger.info("MongoDB disconnected.")


def get_db():
    if db_instance.db is None:
        raise RuntimeError("MongoDB is not connected.")
    return db_instance.db