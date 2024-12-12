from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TargetAudience(str, Enum):
    parents = "parents"
    teachers = "teachers"
    class_specific = "class_specific"
    school_wide = "school_wide"
    class_reps = "class_reps"  # Add this

class AnnouncementBase(BaseModel):
    title: str
    content_en: Optional[str] = None
    content_de: Optional[str] = None
    content_fr: Optional[str] = None
    original_language: str = "en"
    target_audience: TargetAudience
    class_id: int
    recipients: Optional[List[int]] = None

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int
    creator_id: int
    creator_name: Optional[str] = None


    class Config:
        from_attributes = True


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    class_id: int
    class_name: str
    school_name: str
    date_submitted: datetime
    creator_name: str

    class Config:
        orm_mode = True
