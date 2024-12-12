# app/routers/dashboard.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, Class, Announcement, Student, ParentStudent, TeacherClass, School
from app.routers.auth import get_current_user
from typing import List, Dict, Any
from app.schemas.dashboards import AnnouncementResponse
from app.utils.announcement_utils import fetch_announcements, serialize_announcements

router = APIRouter()


@router.get("/dashboard/parent", response_model=Dict[str, Any])
def parent_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "parent":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch ParentStudent relationships for this parent
    parent_student_relationships = db.query(ParentStudent).filter(ParentStudent.parent_id == user.id).all()

    # Fetch the associated students
    student_ids = [ps.student_id for ps in parent_student_relationships]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()

    # If no students are associated, return an empty response for announcements and students
    if not students:
        return {
            "announcements": [],
            "students": []
        }

    # Fetch classes for the children
    class_ids = {student.class_id for student in students}
    classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
    class_map = {cls.id: cls for cls in classes}

    # Fetch announcements for these classes
    announcements = fetch_announcements(
        db=db,
        class_ids=list(class_ids),
        recipient_id=user.id
    )

    # Serialize announcements
    serialized_announcements = serialize_announcements(announcements)

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

    return {
        "announcements": serialized_announcements,
        "students": response_students
    }


@router.get("/dashboard/teacher", response_model=Dict[str, Any])
def teacher_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Teacher Dashboard Endpoint:
    - Fetches teacher profile.
    - Fetches assigned classes, announcements, and available classes.
    """
    # Ensure the user is a teacher
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Load user profile with eager loading
    user_with_profile = (
        db.query(User)
        .options(joinedload(User.profile))
        .filter(User.id == current_user.id)
        .first()
    )

    if not user_with_profile:
        raise HTTPException(status_code=404, detail="User not found")

    # Handle missing profile data
    profile = user_with_profile.profile
    first_name = profile.first_name if profile and profile.first_name else "New"
    last_name = profile.last_name if profile and profile.last_name else "Teacher"
    teacher_name = f"{first_name} {last_name}".strip()

    # Fetch classes assigned to this teacher
    teacher_class_assignments = (
        db.query(TeacherClass)
        .filter(TeacherClass.teacher_id == current_user.id)
        .all()
    )
    assigned_class_ids = [tc.class_id for tc in teacher_class_assignments]

    if not assigned_class_ids:
        # No assigned classes: return all classes as available
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

    # Fetch assigned classes with their schools
    assigned_classes = (
        db.query(Class)
        .filter(Class.id.in_(assigned_class_ids))
        .options(joinedload(Class.school))
        .all()
    )

    # Fetch announcements for assigned classes
    announcements = fetch_announcements(
        db=db, class_ids=assigned_class_ids, recipient_id=current_user.id
    )
    serialized_announcements = serialize_announcements(announcements)

    # Serialize assigned classes for response
    response_classes = [
        {
            "id": c.id,
            "class_name": c.name,
            "school_name": c.school.name,
        }
        for c in assigned_classes
    ]

    return {
        "announcements": serialized_announcements,
        "classes": response_classes,
        "available_classes": [],
        "name": teacher_name,
    }




# Admin Dashboard
@router.get("/dashboard/admin", response_model=Dict[str, Any])
def admin_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch all users, classes, and schools
    users = db.query(User).all()
    classes = db.query(Class).all()
    schools = db.query(School).all()

    # Fetch all announcements with creator names
    announcements = fetch_announcements(db=db)

    # Serialize announcements
    serialized_announcements = serialize_announcements(announcements)

    return {
        "users": users,  # Consider serializing these as well
        "schools": schools,  # Consider serializing these as well
        "classes": classes,  # Consider serializing these as well
        "announcements": serialized_announcements
    }

