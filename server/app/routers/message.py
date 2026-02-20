from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.database import get_db
from app.models import models
from app.schemas import message

message_router = APIRouter()

@message_router.get("/messages/", response_model=List[message.Message])
def get_messages(
    group_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Message).filter(models.Message.group_id == group_id).offset(skip).limit(limit).all()
