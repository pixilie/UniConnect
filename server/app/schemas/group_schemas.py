from typing import Optional

from pydantic import BaseModel


class Group(BaseModel):
    id: int
    name: str
    schedule_path: Optional[str]

class NewGroup(BaseModel):
    name: str
    schedule_path: Optional[str]

class UpdateGroup(BaseModel):
    name: str
    schedule_path: Optional[str]
