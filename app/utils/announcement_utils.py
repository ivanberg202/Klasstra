# app/utils/announcement_utils.py

from sqlalchemy.orm import Session, aliased
from sqlalchemy import or_, func
from app.models import Announcement, Class, User, UserProfile, announcement_recipients
from typing import List, Optional, Dict, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

def serialize_announcements(announcements: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize announcements fetched from the database.

    Expects tuples of:
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
            "recipients": [user.id for user in announcement.recipients]  # List of recipient IDs
        })
    return serialized

def fetch_announcements(
    db: Session,
    class_ids: Optional[List[int]] = None,
    creator_id: Optional[int] = None,
    recipient_id: Optional[int] = None,
    target_audience: Optional[str] = None
) -> List[Any]:
    """
    Fetch announcements based on provided filters.
    Utilizes a normalized many-to-many relationship for recipients.
    """
    
    # Create aliases for User
    CreatorUser = aliased(User, name='creator_user')
    RecipientUser = aliased(User, name='recipient_user')

    # Coalesce for creator name: use UserProfile's first and last name if available; else, use CreatorUser.username
    creator_name = func.coalesce(
        func.concat(UserProfile.first_name, " ", UserProfile.last_name),
        CreatorUser.username
    ).label("creator_name")

    # Base query: Join Announcement with Class, Creator User, and UserProfile
    query = db.query(
        Announcement,
        Class.name.label("class_name"),
        creator_name
    ).join(
        Class, Announcement.class_id == Class.id
    ).join(
        CreatorUser, Announcement.creator_id == CreatorUser.id
    ).outerjoin(
        UserProfile, CreatorUser.id == UserProfile.user_id
    )

    # Apply class_ids filter
    if class_ids:
        query = query.filter(Announcement.class_id.in_(class_ids))
        logger.debug(f"Filtering announcements for class IDs: {class_ids}")

    # Apply creator_id filter
    if creator_id:
        query = query.filter(Announcement.creator_id == creator_id)
        logger.debug(f"Filtering announcements by creator ID: {creator_id}")

    # Apply target_audience filter
    if target_audience:
        query = query.filter(Announcement.target_audience == target_audience)
        logger.debug(f"Filtering announcements for target audience: {target_audience}")

    # Apply recipient_id filter using the many-to-many relationship
    if recipient_id is not None:
        logger.debug(f"Filtering announcements for recipient ID: {recipient_id}")
        # Left outer join to announcement_recipients and RecipientUser
        query = query.outerjoin(
            announcement_recipients,
            Announcement.id == announcement_recipients.c.announcement_id
        ).outerjoin(
            RecipientUser,
            RecipientUser.id == announcement_recipients.c.user_id
        ).filter(
            or_(
                # Announcements with no specific recipients
                announcement_recipients.c.user_id == None,
                # Announcements where the parent is a recipient
                RecipientUser.id == recipient_id
            )
        )
        logger.debug("Applied recipient filter using many-to-many relationship.")

    # Execute the query and fetch all results
    try:
        announcements = query.all()
        logger.debug(f"Number of announcements fetched: {len(announcements)}")
        return announcements
    except Exception as e:
        logger.error(f"Error fetching announcements: {e}")
        raise
