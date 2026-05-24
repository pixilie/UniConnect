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


class Event(BaseModel):
    id: int
    title: str
    description: str
    start: datetime
    end: datetime
    type: str
    location: Optional[str] = None
    creator: CreatorInfo
    group_id: int


class NewEvent(BaseModel):
    title: str
    description: str
    start: datetime
    end: datetime
    type: str
    location: Optional[str] = None


class UpdateEvent(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[datetime] = None
    end: datetime
    type: Optional[str] = None
    location: Optional[str] = None
