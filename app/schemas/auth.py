from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # parent, teacher, admin
    language: str = "en"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    language: str

    class Config:
        from_attributes = True
