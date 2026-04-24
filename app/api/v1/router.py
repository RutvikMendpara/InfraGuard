from fastapi import APIRouter

from app.api.v1.endpoints import findings, scans, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(
    findings.router,
    prefix="/findings",
    tags=["Findings"],
)

api_router.include_router(
    scans.router,
    prefix="/scans",
    tags=["Scans"],
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)