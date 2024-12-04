from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Class, Announcement, Student, ParentStudent, TeacherClass, School
from app.routers.auth import get_current_user
from typing import List


router = APIRouter()

# Parent Dashboard
@router.get("/dashboard/parent")
def parent_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "parent":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch student IDs associated with the parent
    parent_students = db.query(ParentStudent).filter(ParentStudent.parent_id == user.id).all()
    student_ids = [ps.student_id for ps in parent_students]

    # Fetch children (students) and their classes
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    classes = {cls.id: cls for cls in db.query(Class).filter(Class.id.in_([student.class_id for student in students])).all()}

    # Fetch announcements for these classes
    class_ids = list(classes.keys())
    announcements = (
        db.query(Announcement)
        .filter(
            (Announcement.class_id.in_(class_ids)) &
            (
                (Announcement.recipients == None) |  # Announcements to all
                (Announcement.recipients.contains([user.id]))  # Announcements to specific recipients
            )
        )
        .all()
    )

    # Structure the response
    response_students = [
        {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "class": {
                "id": student.class_id,
                "name": classes[student.class_id].name,
            }
        }
        for student in students
    ]

    return {
        "announcements": announcements,
        "students": response_students
    }



# Teacher Dashboard
@router.get("/dashboard/teacher")
def teacher_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Fetch classes taught by the teacher
    class_ids = [tc.class_id for tc in db.query(TeacherClass).filter(TeacherClass.teacher_id == user.id).all()]

    # Fetch announcements for these classes or created by the teacher
    announcements = (
        db.query(Announcement)
        .filter(
            (Announcement.creator_id == user.id) |
            (Announcement.class_id.in_(class_ids))
        )
        .all()
    )

    return {
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
    schools = db.query(School).all()

    return {
        "users": users,
        "schools": schools,
        "classes": classes,
        "announcements": announcements
    }
