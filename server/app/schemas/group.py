from typing import Optional

from pydantic import BaseModel


class Group(BaseModel):
    id: int
    name: str
    schedule_path: Optional[str] = None

class NewGroup(BaseModel):
    name: str
    schedule_path: Optional[str] = None

class UpdateGroup(BaseModel):
    name: Optional[str] = None
