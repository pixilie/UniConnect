from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.models import UserRole


class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    group_id: int | None

    class Config:
        from_attributes = True

class UserUpdateProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

class UserRoleUpdate(BaseModel):
    role: UserRole
