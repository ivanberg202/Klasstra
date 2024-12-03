from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

# Profile-related schemas
class UserProfileBase(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    hobbies: Optional[str]
    preferred_contact_method: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class UserProfileCreate(UserProfileBase):
    pass  # No additional fields required for creation

class UserProfileResponse(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    hobbies: Optional[str]
    preferred_contact_method: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# User-related schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str
    language: Optional[str] = "en"

class UserCreate(UserBase):
    password: str  # Password is required for user creation
    profile: Optional[UserProfileCreate]  # Include profile creation details

class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    role: Optional[str]
    language: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    hobbies: Optional[str]
    preferred_contact_method: Optional[str]

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    language: Optional[str]
    profile: Optional[UserProfileResponse]  # Profile is embedded here

    model_config = ConfigDict(from_attributes=True)