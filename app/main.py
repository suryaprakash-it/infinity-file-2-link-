# app/main.py

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import connect_to_mongo, close_mongo_connection
from app.middleware import InfinitySecurityMiddleware
from app.routes.download import router as download_router
from app.routes.admin import router as admin_router
from bot.bot import app_bot


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown."""

    try:
        logger.info("Starting Infinity Share...")

        # MongoDB
        await connect_to_mongo()
        logger.info("MongoDB connected.")

        # Telegram Bot
        await app_bot.start()
        logger.info("Pyrogram Bot started successfully.")

        yield

    finally:
        logger.info("Shutting down Infinity Share...")

        try:
            await app_bot.stop()
            logger.info("Pyrogram Bot stopped.")
        except Exception:
            logger.exception("Error stopping Pyrogram Bot.")

        try:
            await close_mongo_connection()
            logger.info("MongoDB disconnected.")
        except Exception:
            logger.exception("Error closing MongoDB.")


app = FastAPI(
   