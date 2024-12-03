from pydantic import BaseModel
from typing import Optional


class AnnouncementBase(BaseModel):
    title: str
    content_en: str = None  # Optional for announcements in non-English languages
    content_de: str = None
    content_fr: str = None
    original_language: str = "en"
    target_audience: str
    class_id: int

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int
    creator_id: int

    class Config:
        from_attributes = True  # Update from orm_mode
