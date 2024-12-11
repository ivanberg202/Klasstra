# app/utils/announcement_utils.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.sql import func
from app.models import Announcement, Class, User
from typing import List, Optional, Dict, Any
from datetime import datetime
from typing import List, Dict, Any
from app.models import Announcement, Class, User, UserProfile

def serialize_announcements(announcements: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize announcements fetched from the database.

    Now expects tuples of:
    - Announcement
    - class_name
    - creator_name
    """

    serialized = []
    for announcement, class_name, creator_name in announcements:
        serialized.append({
            "id": announcement.id,
            "title": announcement.title,
            "content_en": announcement.content_en,
            "content_de": announcement.content_de,
            "content_fr": announcement.content_fr,
            "original_language": announcement.original_language,
            "target_audience": announcement.target_audience,
            "class_id": announcement.class_id,
            "class_name": class_name,
            "creator_id": announcement.creator_id,
            "creator_name": creator_name,  # Use combined creator name
            "date_submitted": announcement.created_at.isoformat() if announcement.created_at else None,
            "recipients": announcement.recipients
        })
    return serialized




def fetch_announcements(
    db: Session,
    class_ids: Optional[List[int]] = None,
    creator_id: Optional[int] = None,
    recipient_id: Optional[int] = None,
    target_audience: Optional[str] = None
) -> List[Any]:
    query = db.query(
        Announcement,
        Class.name.label("class_name"),
        func.coalesce(
            func.concat(UserProfile.first_name, " ", UserProfile.last_name),
            User.username
        ).label("creator_name")
    ).join(
        Class, Announcement.class_id == Class.id
    ).join(
        User, Announcement.creator_id == User.id
    ).outerjoin(
        UserProfile, User.id == UserProfile.user_id  # Outer join to handle missing profiles
    )

    filters = []

    if class_ids:
        filters.append(Announcement.class_id.in_(class_ids))
    
    if creator_id:
        filters.append(Announcement.creator_id == creator_id)
    
    if recipient_id is not None:
        # If recipients field is a JSON array or list of user IDs.
        filters.append(
            or_(
                Announcement.recipients == None,
                Announcement.recipients.contains([recipient_id])
            )
        )

    if target_audience:
        filters.append(Announcement.target_audience == target_audience)
    
    if filters:
        query = query.filter(*filters)
    
    return query.all()