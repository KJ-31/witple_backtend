from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.utils.auth import get_current_user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """현재 활성 사용자 가져오기"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """현재 슈퍼유저 가져오기"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
