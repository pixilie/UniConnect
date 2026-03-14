from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)

class Message(BaseModel):
    id: int
    content: str
    message_type: str
    sent_at: datetime
    group_id: int
    author: AuthorInfo
