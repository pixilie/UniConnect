from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class CreatorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class Assignment(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    created_at: datetime
    group_id: int
    creator: CreatorInfo

    class Config:
        from_attributes = True


class NewAssignment(BaseModel):
    title: str
    description: str
    group_id: int
    due_date: datetime


class UpdateAssignment(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
