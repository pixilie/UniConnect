from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreatorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)

class Announcement(BaseModel):
    id: int
    title: str
    content: str
    due_date: datetime
    created_at: datetime
    urgent: bool
    group_id: int
    creator: CreatorInfo

    class Config:
            from_attributes = True

class NewAnnoucement(BaseModel):
    title: str
    content: str
    urgent: bool
