from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.utils.auth import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """사용자 회원가입"""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 사용자명 중복 확인
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # 새 사용자 생성
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        bio=user_data.bio,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """사용자 로그인"""
    # 사용자 찾기 (이메일 또는 사용자명으로)
    user = db.query(User).filter(
        (User.email == login_data.username) | (User.username == login_data.username)
    ).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 액세스 토큰 생성
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """사용자 로그아웃"""
    # JWT는 stateless이므로 클라이언트에서 토큰을 삭제하면 됩니다
    # 필요시 블랙리스트에 토큰을 추가할 수 있습니다
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return current_user
