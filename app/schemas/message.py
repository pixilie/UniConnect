from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    id: int
    content: str
    message_type: str
    sent_at: datetime
    user_id: int
    group_id: int
