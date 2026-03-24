from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class AuthorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class Message(BaseModel):
    id: int
    content: str
    sent_at: datetime
    group_id: int
    author: AuthorInfo
