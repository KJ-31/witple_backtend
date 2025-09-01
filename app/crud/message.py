from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate
from typing import List, Optional


def create_message(db: Session, message: MessageCreate) -> Message:
    """메시지 생성"""
    db_message = Message(content=message.content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages(db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
    """메시지 목록 조회"""
    return db.query(Message).offset(skip).limit(limit).all()


def get_message(db: Session, message_id: int) -> Optional[Message]:
    """특정 메시지 조회"""
    return db.query(Message).filter(Message.id == message_id).first()


def update_message(db: Session, message_id: int, message: MessageUpdate) -> Optional[Message]:
    """메시지 수정"""
    db_message = get_message(db, message_id)
    if db_message:
        update_data = message.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_message, field, value)
        db.commit()
        db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int) -> bool:
    """메시지 삭제"""
    db_message = get_message(db, message_id)
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False
