from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "ok",
        "message": "Backend is running",
        "environment": settings.environment
    }


@router.get("/version")
async def get_version():
    """버전 정보 엔드포인트"""
    return {
        "version": settings.version,
        "app_name": settings.app_name
    }
