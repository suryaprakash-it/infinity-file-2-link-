# app/main.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database import connect_to_mongo, close_mongo_connection
from bot.bot import app_bot
from app.routes.download import router as download_router
from app.middleware import InfinitySecurityMiddleware  # Imported Phase 6 Security

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Pool & MTProto Bot Engine
    await connect_to_mongo()
    await app_bot.start()
    logger.info("🤖 Pyrogram Bot started successfully.")
    yield
    # Shutdown: Cleanly offload resources
    await app_bot.stop()
    logger.info("🤖 Pyrogram Bot stopped.")
    await close_mongo_connection()

# 1. Initialize core FastAPI framework
app = FastAPI(
    title="Infinity Share API",
    lifespan=lifespan
)

# 2. Add Phase 6 Security Middleware (Rate limits & Hardened Headers)
app.add_middleware(InfinitySecurityMiddleware)

# 3. Mount static directory for high-fidelity styles/scripts
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. Include routing systems
app.include_router(download_router, tags=["Downloads"])

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Infinity Share Engine Online"}
