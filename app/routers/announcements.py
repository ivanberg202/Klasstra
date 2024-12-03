from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Announcement, User
from app.schemas.announcements import AnnouncementCreate, AnnouncementResponse
from app.routers.auth import get_current_user


router = APIRouter()

@router.post("announcements/create", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Check if user has permission to post (teacher or class representative)
    if user.role not in ["teacher", "class_representative"]:
        raise HTTPException(status_code=403, detail="Not authorized to post announcements")
    
    # Create announcement
    new_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        language=announcement.language,
        creator_id=user.id,
        class_id=announcement.class_id,
        target_audience=announcement.target_audience,
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement
