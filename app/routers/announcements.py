# app/routers/announcements.py

from fastapi.logger import logger
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models import (
    Announcement,
    User,
    Class,
    teacher_class,
    ClassRepresentative,
    ParentStudent,
    Student,
)
from app.schemas.announcements import AnnouncementCreate, AnnouncementResponse, AnnouncementOut
from app.routers.auth import get_current_user

router = APIRouter()


@router.post("/announcements/create", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new announcement.
    - Admins: Can assign to any user.
    - Teachers: Can assign to any user or specific recipients.
    - Class Representatives: Can assign to class representatives within their school.
    """
    # Validate user role
    if user.role not in ["teacher", "class_representative", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to post announcements")

    # Get classes the user is assigned to
    if user.role == "teacher":
        valid_class_ids = [
            tc.class_id for tc in db.query(teacher_class).filter(teacher_class.c.teacher_id == user.id).all()
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

    # Initialize recipients list
    recipients = []

    # Validate recipients if provided
    if announcement.recipients:
        if announcement.target_audience == "class_reps":
            # Get class reps in the same school
            allowed_recipients = get_class_reps_in_school(user, db)
            if not set(announcement.recipients).issubset(set(allowed_recipients)):
                raise HTTPException(status_code=403, detail="Invalid recipients selected")
            # Fetch User instances for recipients
            recipients = db.query(User).filter(User.id.in_(announcement.recipients)).all()
        else:
            # For other audiences, validate recipients as parents in the class
            allowed_parents = get_allowed_parents(announcement.class_id, db)
            if not set(announcement.recipients).issubset(set(allowed_parents)):
                raise HTTPException(status_code=403, detail="Invalid recipients selected")
            # Fetch User instances for recipients
            recipients = db.query(User).filter(User.id.in_(announcement.recipients)).all()

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
        recipients=recipients,  # Assign list of User instances
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


@router.get("/announcements", response_model=List[AnnouncementOut])
def get_announcements(
    class_ids: List[int] = Query(..., description="List of class IDs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve announcements for specified class IDs.
    """
    try:
        # Log input parameters
        logger.info(f"Received request to fetch announcements for class IDs: {class_ids} by user: {current_user.id}")

        if not class_ids:
            logger.warning("class_ids parameter is missing")
            raise HTTPException(status_code=400, detail="class_ids parameter is required")

        # Fetch announcements with related class and creator
        announcements = (
            db.query(Announcement)
            .options(joinedload(Announcement.class_), joinedload(Announcement.creator))
            .filter(Announcement.class_id.in_(class_ids))
            .all()
        )

        logger.info(f"Fetched {len(announcements)} announcements from the database.")

        if not announcements:
            logger.info("No announcements found for the given class IDs.")
            return []

        # Serialize announcements
        serialized_announcements = []
        for announcement in announcements:
            content = (
                announcement.content_de
                or announcement.content_en
                or announcement.content_fr
                or "No content available."
            )

            creator_name = announcement.creator.username if announcement.creator else "Unknown Creator"

            serialized_announcement = AnnouncementOut(
                id=announcement.id,
                title=announcement.title,
                content=content,
                class_id=announcement.class_id,
                class_name=announcement.class_.name if announcement.class_ else "Unknown Class",
                school_name=announcement.class_.school.name if announcement.class_ and announcement.class_.school else "Unknown School",
                date_submitted=announcement.created_at,
                creator_name=creator_name,
            )
            serialized_announcements.append(serialized_announcement)

        logger.info(f"Serialized announcements: {serialized_announcements}")
        return serialized_announcements

    except Exception as e:
        logger.error(f"Error occurred in /announcements endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch announcements")
