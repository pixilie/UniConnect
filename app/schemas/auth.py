from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints

StrictName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[A-Za-zÀ-ÿ\-]+$"
    )
]

class NewUser(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True

class RegistrationRequest(BaseModel):
    first_name: StrictName
    last_name: StrictName
    email: EmailStr
    password: str
