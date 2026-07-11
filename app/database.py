from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    # Connection pooling configuration optimized for concurrent lookups
    db_instance.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize=100,
        minPoolSize=10,
        maxIdleTimeMS=10000
    )
    # Extract database name from URI or default
    db_name = settings.MONGO_URI.split('/')[-1].split('?')[0] or "infinity_share"
    db_instance.db = db_instance.client[db_name]
    
    # Create indexes for blazing fast query performance (Phase 8 optimization)
    await db_instance.db.files.create_index("file_id", unique=True)
    await db_instance.db.files.create_index("custom_alias", unique=True, sparse=True)
    await db_instance.db.users.create_index("user_id", unique=True)
    logger.info("MongoDB connected and indexes verified.")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    if db_instance.client:
        db_instance.client.close()
    logger.info("MongoDB disconnected.")

def get_db():
    return db_instance.db
