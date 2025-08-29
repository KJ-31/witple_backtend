from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.utils.auth import get_current_user, get_password_hash
from app.utils.security import get_current_active_user

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """사용자 프로필 조회"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 프로필 수정"""
    # 이메일 중복 확인 (다른 사용자와 중복되지 않는지)
    if user_data.email and user_data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 사용자명 중복 확인
    if user_data.username and user_data.username != current_user.username:
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # 사용자 정보 업데이트
    update_data = user_data.dict(exclude_unset=True)
    
    # 비밀번호가 제공된 경우 해싱
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """비밀번호 변경"""
    from app.utils.auth import verify_password
    
    # 현재 비밀번호 확인
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # 새 비밀번호로 업데이트
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
