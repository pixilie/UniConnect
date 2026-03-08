from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True

class RegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
