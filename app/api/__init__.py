from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .health import router as health_router

# API 라우터 생성
api_router = APIRouter(prefix="/api/v1")

# 라우터 등록
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
