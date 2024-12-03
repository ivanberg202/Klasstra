from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ClassResponse(BaseModel):
    id: int
    name: str
    school_id: int

    model_config = ConfigDict(from_attributes=True)

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content_en: str
    class_id: int

    model_config = ConfigDict(from_attributes=True)

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
