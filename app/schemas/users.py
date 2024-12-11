from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ------------------------------
# Student-related schemas
# ------------------------------
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    class_id: int  # Class ID the student is enrolled in

    class Config:
        orm_mode = True


class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    class_id: int

    class Config:
        orm_mode = True

# ------------------------------
# User profile-related schemas
# ------------------------------
class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    hobbies: Optional[str] = None
    preferred_contact_method: Optional[str] = None

    class Config:
        orm_mode = True


class UserProfileCreate(UserProfileBase):
    # No additional fields; inherits all optional fields from UserProfileBase
    class Config:
        orm_mode = True
        from_attributes = True  # Required for `from_orm`



class UserProfileResponse(UserProfileBase):
    # Add any related fields (e.g. school, class, etc.) if needed in future
    class Config:
        orm_mode = True

# ------------------------------
# Parent-student relationship schema
# ------------------------------
class ParentStudentResponse(BaseModel):
    parent_id: int
    student_id: int
    relationship_type: Optional[str] = None

    class Config:
        orm_mode = True

# ------------------------------
# Teacher-class assignment schema
# ------------------------------
class TeacherClassAssignment(BaseModel):
    teacher_id: int
    class_id: int

    class Config:
        orm_mode = True

# ------------------------------
# User-related schemas
# ------------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str  # 'admin', 'teacher', 'parent'
    language: Optional[str] = "en"

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # admin, teacher, parent

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    language: Optional[str] = None
    profile: Optional[UserProfileCreate] = None  # Profile is optional
    students: Optional[List[StudentCreate]] = None  # For updating parent students

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str  # 'admin', 'teacher', 'parent'

    class Config:
        orm_mode = True
        from_attributes = True  # Required for `from_orm`
