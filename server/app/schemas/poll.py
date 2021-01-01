from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChoiceBase(BaseModel):
    text: str
    manifesto: str | None = None
    photo_url: str | None = None

class ChoiceResponse(ChoiceBase):
    id: int
    poll_id: int | None
    model_config = ConfigDict(from_attributes=True)

class PollCreate(BaseModel):
    title: str

class PollResponse(BaseModel):
    id: int
    title: str
    is_active: bool
    created_at: datetime
    group_id: int | None
    choices: list[ChoiceResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ChoiceResult(ChoiceBase):
    id: int
    vote_count: int

class PollResultResponse(BaseModel):
    poll_id: int
    title: str
    is_active: bool
    total_votes: int
    results: list[ChoiceResult]
