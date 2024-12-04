# app/routers/announcements.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import (
    Announcement,
    User,
    Class,
    TeacherClass,
    ClassRepresentative,
    ParentStudent,
    Student,
)
from app.schemas.announcements import AnnouncementCreate, AnnouncementResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/announcements/create", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate user role
    if user.role not in ["teacher", "class_representative", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to post announcements")

    # Get classes the user is assigned to
    if user.role == "teacher":
        valid_class_ids = [
            tc.class_id for tc in db.query(TeacherClass).filter(TeacherClass.teacher_id == user.id).all()
        ]
    elif user.role == "class_representative":
        valid_class_ids = [
            cr.class_id for cr in db.query(ClassRepresentative).filter(ClassRepresentative.parent_id == user.id).all()
        ]
    else:
        valid_class_ids = []

    # Check if the user is allowed to post in the class
    if announcement.class_id not in valid_class_ids and user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not assigned to this class")

    # Validate recipients if provided
    if announcement.recipients:
        # If target audience is 'class_reps', use the provided code snippet
        if announcement.target_audience == "class_reps":
            allowed_recipients = get_class_reps_in_school(user, db)
            if not set(announcement.recipients).issubset(set(allowed_recipients)):
                raise HTTPException(status_code=403, detail="Invalid recipients selected")
        else:
            # For other audiences, validate recipients as parents in the class
            allowed_parents = get_allowed_parents(announcement.class_id, db)
            if not set(announcement.recipients).issubset(set(allowed_parents)):
                raise HTTPException(status_code=403, detail="Invalid recipients selected")

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
        recipients=announcement.recipients,
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement

# Helper function to get allowed parents in a class
def get_allowed_parents(class_id: int, db: Session) -> List[int]:
    parent_ids = db.query(ParentStudent.parent_id).join(Student).filter(Student.class_id == class_id).all()
    # Flatten the list of tuples
    return [pid[0] for pid in parent_ids]

# Helper function to get class reps in the same school
def get_class_reps_in_school(user: User, db: Session) -> List[int]:
    # Get class IDs where the user is a class rep
    class_ids = [
        cr.class_id for cr in db.query(ClassRepresentative).filter(ClassRepresentative.parent_id == user.id).all()
    ]
    if not class_ids:
        return []

    # Get the school IDs associated with these classes
    school_ids = [
        c.school_id for c in db.query(Class).filter(Class.id.in_(class_ids)).all()
    ]

    # Get all class reps in these schools
    class_rep_ids = [
        cr.parent_id for cr in db.query(ClassRepresentative)
        .join(Class, Class.id == ClassRepresentative.class_id)
        .filter(Class.school_id.in_(school_ids))
        .all()
    ]

    # Remove duplicates and exclude the current user
    class_rep_ids = list(set(class_rep_ids))
    if user.id in class_rep_ids:
        class_rep_ids.remove(user.id)

    return class_rep_ids
