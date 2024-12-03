from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str
    language: str = "en"

class UserCreate(UserBase):
    password: str

class UserProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: str
    hobbies: str
    preferred_contact_method: str
