from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import models


class ResourceResponse(BaseModel):
    id: int
    title: str
    file_path: str
    file_type: str | None
    category: models.ResourceCategory
    uploaded_at: datetime
    user_id: int | None
    group_id: int | None

    model_config = ConfigDict(from_attributes=True)
