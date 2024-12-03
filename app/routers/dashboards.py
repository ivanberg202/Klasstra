from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Class, Announcement, Student, ParentStudent, TeacherClass
from app.routers.auth import get_current_user

router = APIRouter()

# Parent Dashboard
@router.get("/dashboard/parent")
def parent_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "parent":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch students associated with the parent
    student_ids = db.query(ParentStudent.student_id).filter(ParentStudent.parent_id == user.id).subquery()

    # Fetch classes where the parent's children are enrolled
    child_classes = (
        db.query(Class)
        .join(Student, Student.class_id == Class.id)
        .filter(Student.id.in_(student_ids))
        .all()
    )

    # Fetch announcements for these classes
    announcements = (
        db.query(Announcement)
        .filter(Announcement.class_id.in_([cls.id for cls in child_classes]))
        .all()
    )

    return {
        "classes": child_classes,
        "announcements": announcements
    }


# Teacher Dashboard
@router.get("/dashboard/teacher")
def teacher_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch classes taught by the teacher using the TeacherClass association table
    teacher_classes = (
        db.query(Class)
        .join(TeacherClass, TeacherClass.class_id == Class.id)
        .filter(TeacherClass.teacher_id == user.id)
        .all()
    )

    # Fetch announcements created by the teacher
    announcements = db.query(Announcement).filter(Announcement.creator_id == user.id).all()

    return {
        "classes": teacher_classes,
        "announcements": announcements
    }


# Admin Dashboard
@router.get("/dashboard/admin")
def admin_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch all users, classes, and announcements
    users = db.query(User).all()
    classes = db.query(Class).all()
    announcements = db.query(Announcement).all()

    return {
        "users": users,
        "classes": classes,
        "announcements": announcements
    }
