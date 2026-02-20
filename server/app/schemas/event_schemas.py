from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    id: int
    title: str
    desription: str
    date: datetime
    type: str
    location: str
    latitude: float
    longitude: float
    creator_id: int
    group_id: int

class NewEvent(BaseModel):
    title: str
    desription: str
    date: datetime
    type: str
    location: str

class UpdateEvent(BaseModel):
    title: Optional[str] = None
    desription: Optional[str] = None
    date: Optional[datetime] = None
    type: Optional[str] = None
    location: Optional[str] = None
