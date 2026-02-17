from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Assignment(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    created_at: datetime
    class_id: int
    creator_id: int

    class Config:
            from_attributes = True

class NewAssignment(BaseModel):
    title: str
    description: str
    class_id: int
    due_date: datetime

class UpdateAssignment(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
