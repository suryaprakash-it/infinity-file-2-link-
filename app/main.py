from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB Connection Pool
    await connect_to_mongo()
    yield
    # Shutdown: Cleanly close pools
    await close_mongo_connection()

app = FastAPI(
    title="Infinity Share API",
    description="High-performance, async backend for Telegram file streaming",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Infinity Share API"}
