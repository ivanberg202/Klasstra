from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Announcement, User, Class
from app.schemas.announcements import AnnouncementCreate, AnnouncementResponse
from app.routers.auth import get_current_user
from app.schemas.classes import ClassCreate, ClassResponse


router = APIRouter()


@router.post("/announcements/create", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Check if user has permission to post
    if user.role not in ["teacher", "class_representative"]:
        raise HTTPException(status_code=403, detail="Not authorized to post announcements")
    
    # Validate that the class_id exists
    class_exists = db.query(Class).filter(Class.id == announcement.class_id).first()
    if not class_exists:
        raise HTTPException(
            status_code=400,
            detail=f"Class with id {announcement.class_id} does not exist"
        )
    
    # Create announcement
    new_announcement = Announcement(
        title=announcement.title,
        content_en=announcement.content_en,
        content_de=announcement.content_de,
        content_fr=announcement.content_fr,
        original_language=announcement.original_language,
        creator_id=user.id,
        class_id=announcement.class_id,
        target_audience=announcement.target_audience,
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement
