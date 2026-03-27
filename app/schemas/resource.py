from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import ResourceCategory, UserRole


class UploaderInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class ResourceResponse(BaseModel):
    id: int
    title: str
    file_path: str
    file_type: str | None
    category: ResourceCategory
    uploaded_at: datetime
    uploader: UploaderInfo
    group_id: int

    model_config = ConfigDict(from_attributes=True)
