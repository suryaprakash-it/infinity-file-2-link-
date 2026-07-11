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
            or "infinity