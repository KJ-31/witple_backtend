from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행될 코드"""
    # 시작 시 데이터베이스 초기화
    init_db()
    print("🚀 Witple Backend API started!")
    yield
    print("👋 Witple Backend API stopped!")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Witple Backend API - FastAPI 기반 백엔드 서버",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Welcome to Witple Backend API!",
        "version": settings.version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/docs")
async def get_docs():
    """API 문서 링크"""
    return {
        "message": "API Documentation",
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json"
    }
