from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.message import Message, MessageCreate, MessageUpdate
from app.crud import message as message_crud

router = APIRouter()


@router.post("/", response_model=Message, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """메시지 생성"""
    return message_crud.create_message(db=db, message=message)


@router.get("/", response_model=List[Message])
def get_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """메시지 목록 조회"""
    messages = message_crud.get_messages(db, skip=skip, limit=limit)
    return messages


@router.get("/{message_id}", response_model=Message)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """특정 메시지 조회"""
    message = message_crud.get_message(db, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다")
    return message


@router.put("/{message_id}", response_model=Message)
def update_message(message_id: int, message: MessageUpdate, db: Session = Depends(get_db)):
    """메시지 수정"""
    updated_message = message_crud.update_message(db, message_id=message_id, message=message)
    if updated_message is None:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다")
    return updated_message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """메시지 삭제"""
    success = message_crud.delete_message(db, message_id=message_id)
    if not success:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다")
    return None
