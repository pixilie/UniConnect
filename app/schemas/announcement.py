from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class CreatorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class Announcement(BaseModel):
    id: int
    title: str
    content: str
    sent_at: datetime
    urgent: bool
    group_id: int
    author: CreatorInfo

    model_config = ConfigDict(from_attributes=True)


class NewAnnoucement(BaseModel):
    title: str
    content: str
    urgent: bool
