from typing import Annotated, List, Optional

from pydantic import BaseModel, EmailStr, StringConstraints

StrictName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[A-Za-zÀ-ÿ\-]+$"),
]


class Group(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    groups: List[Group] = []

    class Config:
        from_attributes = True


class UserUpdateProfile(BaseModel):
    first_name: Optional[StrictName] = None
    last_name: Optional[StrictName] = None
    email: Optional[EmailStr] = None


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
