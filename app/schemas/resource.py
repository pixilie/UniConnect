from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import models


class AuthorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)

class ResourceResponse(BaseModel):
    id: int
    title: str
    file_path: str
    file_type: str | None
    category: models.ResourceCategory
    uploaded_at: datetime
    author: AuthorInfo
    group_id: int

    model_config = ConfigDict(from_attributes=True)
