from typing import List, Optional

from pydantic import BaseModel, EmailStr


class RegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True

class UserUpdateProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

class UserUpdateAdmin(BaseModel):
    role: Optional[str] = None
    student_class_id: Optional[int] = None
    teaching_class_ids: Optional[List[int]] = None
