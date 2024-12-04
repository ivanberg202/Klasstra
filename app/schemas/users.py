from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List

# Profile-related schemas
class UserProfileBase(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    hobbies: Optional[str]
    preferred_contact_method: Optional[str]

    school_id: Optional[int] = None
    class_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileCreate(UserProfileBase):
    students: Optional[List['StudentCreate']] = None  # List of students

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserProfileBase):
    students: Optional[List['StudentResponse']] = None  # Include student details in the response

    model_config = ConfigDict(from_attributes=True)

# User-related schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str
    language: Optional[str] = "en"

class UserCreate(UserBase):
    password: str  # Password is required for user creation
    profile: Optional[UserProfileCreate]  # Include nested profile schema

class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    role: Optional[str]
    language: Optional[str]
    profile: Optional[UserProfileCreate]  # Use the same profile schema as in `UserCreate`

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    language: Optional[str]
    profile: Optional[UserProfileResponse]  # Embed profile details in the response

    model_config = ConfigDict(from_attributes=True)


# Schemas for students
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    class_id: int  # Class ID the student is enrolled in

class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    class_id: int  # Class ID the student is enrolled in

    model_config = ConfigDict(from_attributes=True)
