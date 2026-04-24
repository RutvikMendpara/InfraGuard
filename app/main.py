from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logger import logger

from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting InfraGuard API")

    try:
        init_db() 
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init failed: {e}")
        raise

    yield

    logger.info("Shutting down InfraGuard API")


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.include_router(api_router)