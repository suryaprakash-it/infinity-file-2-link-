# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.database import connect_to_mongo, close_mongo_connection
from bot.bot import app_bot
from app.routes.download import router as download_router # <-- ADD THIS IMPORT

# Insert this statement inside app/main.py along with other imports:
from fastapi.staticfiles import StaticFiles

# Add this command right right above app.include_router(download_router):
app.mount("/static", StaticFiles(directory="static"), name="static")


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await app_bot.start()
    logger.info("🤖 Pyrogram Bot started successfully.")
    yield
    await app_bot.stop()
    logger.info("🤖 Pyrogram Bot stopped.")
    await close_mongo_connection()

app = FastAPI(
    title="Infinity Share API",
    lifespan=lifespan
)

# <-- ADD THIS LINE TO REGISTER THE DOWNLOAD ENGINE -->
app.include_router(download_router, tags=["Downloads"])

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Infinity Share Engine Online"}
