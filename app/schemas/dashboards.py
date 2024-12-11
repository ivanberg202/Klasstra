from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ClassResponse(BaseModel):
    id: int
    name: str
    school_id: int

    model_config = ConfigDict(from_attributes=True)

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content_en: Optional[str] = None
    content_de: Optional[str] = None
    content_fr: Optional[str] = None
    original_language: str
    target_audience: str
    class_id: int
    class_name: str
    creator_id: int
    creator_name: str
    date_submitted: Optional[datetime] = None
    recipients: Optional[List[int]] = None

    class Config:
        orm_mode = True

class ParentDashboardResponse(BaseModel):
    classes: List[ClassResponse]
    announcements: List[AnnouncementResponse]

class TeacherDashboardResponse(BaseModel):
    classes: List[ClassResponse]
    announcements: List[AnnouncementResponse]

class AdminDashboardResponse(BaseModel):
    users: List[dict]  # Adjust based on your user schema
    classes: List[ClassResponse]
    announcements: List[AnnouncementResponse]
