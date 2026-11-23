"""Health check routes"""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("", response_model=dict)
async def health_check() -> dict:
    return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION}
