from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    type: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    creator_id: int
    group_id: int

class NewEvent(BaseModel):
    title: str
    description: str
    date: datetime
    type: str
    location: Optional[str] = None

class UpdateEvent(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    type: Optional[str] = None
    location: Optional[str] = None
