from pydantic import BaseModel
from typing import Optional


class AnnouncementBase(BaseModel):
    title: str
    content: str
    language: str
    target_audience: str  # e.g., 'parents', 'teachers'

class AnnouncementCreate(AnnouncementBase):
    class_id: int

class AnnouncementResponse(AnnouncementBase):
    id: int
    creator_id: int

    class Config:
        from_attributes = True  # Update from orm_mode
