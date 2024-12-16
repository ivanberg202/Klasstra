# app/routers/dashboard.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, Class, Announcement, Student, ParentStudent, teacher_class, School
from app.routers.auth import get_current_user
from typing import List, Dict, Any
from app.schemas.dashboards import AnnouncementResponse
from app.utils.announcement_utils import fetch_announcements, serialize_announcements
import logging


router = APIRouter()

logger = logging.getLogger(__name__)



@router.get("/dashboard/parent", response_model=Dict[str, Any])
def parent_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.debug(f"User ID: {user.id}, Role: {user.role}")

    if user.role != "parent":
        logger.warning(f"User ID {user.id} attempted to access parent dashboard without proper role.")
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch ParentStudent relationships for this parent
    parent_student_relationships = db.query(ParentStudent).filter(ParentStudent.parent_id == user.id).all()
    student_ids = [ps.student_id for ps in parent_student_relationships]
    logger.debug(f"Student IDs associated with parent {user.id}: {student_ids}")

    # Fetch the associated students
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    logger.debug(f"Fetched {len(students)} students for parent {user.id}")

    # If no students are associated, return an empty response for announcements and students
    if not students:
        logger.info(f"No students associated with parent {user.id}. Returning empty announcements and students.")
        return {
            "announcements": [],
            "students": []
        }

    # Fetch classes for the children
    class_ids = {student.class_id for student in students}
    classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
    class_map = {cls.id: cls for cls in classes}
    logger.debug(f"Class IDs associated with parent {user.id}: {class_ids}")

    # Fetch announcements for these classes and the parent as recipient
    announcements = fetch_announcements(
        db=db,
        class_ids=list(class_ids),
        recipient_id=user.id
    )
    logger.debug(f"Fetched {len(announcements)} announcements for parent {user.id}")

    # Serialize announcements
    serialized_announcements = serialize_announcements(announcements)
    logger.debug(f"Serialized announcements: {serialized_announcements}")

    # Serialize students and their classes
    response_students = [
        {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "class": {
                "id": student.class_id,
                "name": class_map[student.class_id].name if student.class_id in class_map else "Unknown",
            }
        }
        for student in students
    ]
    logger.debug(f"Serialized students: {response_students}")

    return {
        "announcements": serialized_announcements,
        "students": response_students
    }

@router.get("/dashboard/teacher", response_model=Dict[str, Any])
def teacher_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.debug(f"User ID: {current_user.id}, Role: {current_user.role}")

    # Ensure the user is a teacher
    if current_user.role != "teacher":
        logger.warning(f"User ID {current_user.id} attempted to access teacher dashboard without proper role.")
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Load user profile
    user_with_profile = (
        db.query(User)
        .options(joinedload(User.profile))
        .filter(User.id == current_user.id)
        .first()
    )

    if not user_with_profile:
        logger.error(f"User {current_user.id} not found in the database.")
        raise HTTPException(status_code=404, detail="User not found")

    profile = user_with_profile.profile
    first_name = profile.first_name if profile and profile.first_name else "New"
    last_name = profile.last_name if profile and profile.last_name else "Teacher"
    teacher_name = f"{first_name} {last_name}".strip()
    logger.debug(f"Teacher name resolved as: {teacher_name}")

    # Fetch classes assigned to this teacher (via teacher_id in teacher_class table)
    teacher_class_assignments = (
        db.query(teacher_class)
        .filter(teacher_class.c.teacher_id == current_user.id)  # Corrected to use .c
        .all()
    )
    assigned_class_ids = [tc.class_id for tc in teacher_class_assignments]
    logger.debug(f"Assigned class IDs for teacher {current_user.id}: {assigned_class_ids}")

    # If no assigned classes, return all as available
    if not assigned_class_ids:
        logger.info(f"No classes assigned to teacher {current_user.id}. Returning all classes as available.")
        all_classes = db.query(Class).options(joinedload(Class.school)).all()
        available_classes = [
            {
                "id": c.id,
                "class_name": c.name,
                "school_name": c.school.name,
            }
            for c in all_classes
        ]

        return {
            "announcements": [],
            "classes": [],
            "available_classes": available_classes,
            "name": teacher_name,
        }

    # If there are assigned classes, fetch them
    assigned_classes = (
        db.query(Class)
        .filter(Class.id.in_(assigned_class_ids))
        .options(joinedload(Class.school))
        .all()
    )
    logger.debug(f"Fetched {len(assigned_classes)} assigned classes for teacher {current_user.id}.")

    # Fetch all classes to determine available classes
    all_classes = db.query(Class).options(joinedload(Class.school)).all()
    all_class_ids = {c.id for c in all_classes}
    available_class_ids = all_class_ids - set(assigned_class_ids)
    logger.debug(f"Available class IDs for teacher {current_user.id}: {available_class_ids}")

    available_classes = [
        {
            "id": c.id,
            "class_name": c.name,
            "school_name": c.school.name,
        }
        for c in all_classes if c.id in available_class_ids
    ]

    # Fetch announcements for the assigned classes
    announcements = fetch_announcements(
        db=db, 
        class_ids=assigned_class_ids, 
        recipient_id=current_user.id
    )
    logger.debug(f"Fetched {len(announcements)} announcements for teacher {current_user.id}.")
    serialized_announcements = serialize_announcements(announcements)
    logger.debug(f"Serialized announcements: {serialized_announcements}")

    # Serialize assigned classes
    response_classes = [
        {
            "id": c.id,
            "class_name": c.name,
            "school_name": c.school.name,
        }
        for c in assigned_classes
    ]
    logger.debug(f"Serialized assigned classes: {response_classes}")

    return {
        "announcements": serialized_announcements,
        "classes": response_classes,
        "available_classes": available_classes,
        "name": teacher_name,
    }
