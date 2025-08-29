from sqlalchemy import Column, String, Boolean, Text
from .base import BaseModel


class User(BaseModel):
    """사용자 모델"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    bio = Column(Text)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
