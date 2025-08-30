from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # 기본 설정
    app_name: str = "Witple Backend API"
    version: str = "1.0.0"
    environment: str = "development"
    
    # 데이터베이스 설정
    database_url: str = "postgresql://witple_user:witple_password@localhost:5432/witple"
    
    # Redis 설정
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # JWT 설정
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS 설정 (문자열로 받아서 내부에서 파싱)
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """allowed_origins를 리스트로 변환"""
        if not self.allowed_origins:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        
        origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        return origins if origins else ["http://localhost:3000", "http://127.0.0.1:3000"]


# 환경별 설정
def get_settings():
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return Settings(
            database_url=os.getenv("DATABASE_URL", "postgresql://witple_user:witple_password@postgres:5432/witple"),
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379"),
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        )
    else:
        return Settings(
            database_url=os.getenv("DATABASE_URL", "postgresql://witple_user:witple_password@localhost:5432/witple"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
        )


settings = get_settings()
