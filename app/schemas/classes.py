# app/schemas/classes.py

from pydantic import BaseModel
from typing import Optional

class ClassBase(BaseModel):
    name: str  # Changed from 'class_name' to 'name' to match ORM model
    school_id: int

    class Config:
        orm_mode = True

class ClassCreate(ClassBase):
    pass

class ClassResponse(BaseModel):
    id: int
    class_name: str
    school_id: int
    school_name: str  # Include school_name to simplify API responses

    class Config:
        orm_mode = True

class ClassAssignmentRequest(BaseModel):
    class_id: int