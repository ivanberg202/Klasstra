from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Class, User, TeacherClass, Student, ParentStudent, ClassRepresentative
from app.schemas.classes import ClassCreate, ClassResponse
from app.schemas.users import TeacherClassAssignment
from app.routers.auth import role_required, get_current_user
from typing import List

router = APIRouter()


@router.get('/classes/my-classes', response_model=List[ClassResponse])
def get_my_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):    
    print(f"Current user: ID={current_user.id}, Role={current_user.role}")
    print(f"User profile: {current_user.profile}")
    if current_user.role == 'teacher':
        # Fetch classes assigned to the teacher
        classes = db.query(Class).filter(
            Class.id.in_(
                db.query(TeacherClass.class_id).filter(
                    TeacherClass.teacher_id == current_user.id
                )
            )
        ).all()
    elif current_user.role == 'parent':
        # Fetch classes of the parent's children
        classes = db.query(Class).filter(
            Class.id.in_(
                db.query(Student.class_id).filter(
                    Student.id.in_(
                        db.query(ParentStudent.student_id).filter(
                            ParentStudent.parent_id == current_user.id
                        )
                    )
                )
            )
        ).all()
    elif current_user.role == 'class_representative':
        # Fetch the class where the user is a representative
        classes = db.query(Class).filter(
            Class.id.in_(
                db.query(ClassRepresentative.class_id).filter(
                    ClassRepresentative.parent_id == current_user.id
                )
            )
        ).all()
    elif current_user.role == 'admin':
        # Admins can see all classes
        classes = db.query(Class).all()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return classes



@router.post("/classes/create", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    existing_class = db.query(Class).filter(Class.name == class_data.name, Class.school_id == class_data.school_id).first()
    if existing_class:
        raise HTTPException(status_code=400, detail="Class already exists in this school")
    new_class = Class(name=class_data.name, school_id=class_data.school_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@router.get("/classes/{class_id}", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def get_class(class_id: int, db: Session = Depends(get_db)):
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_


@router.put("/classes/{class_id}/update", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def update_class(class_id: int, class_data: ClassCreate, db: Session = Depends(get_db)):
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    class_.name = class_data.name
    class_.school_id = class_data.school_id
    db.commit()
    db.refresh(class_)
    return class_


@router.delete("/classes/{class_id}", dependencies=[Depends(role_required("admin"))])
def delete_class(class_id: int, db: Session = Depends(get_db)):
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(class_)
    db.commit()
    return {"message": "Class deleted successfully"}


@router.post("/teacher-class-assignments", response_model=dict)
def assign_class_to_teacher(
    assignment: TeacherClassAssignment,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)  # Allow both admin and teacher
):
    # Check if user is admin or teacher
    if user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # If the user is a teacher, ensure they can only assign themselves
    if user.role == "teacher" and assignment.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Teachers can only assign themselves to classes")

    # Validate teacher
    teacher = db.query(User).filter(User.id == assignment.teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found or not a teacher")

    # Validate class
    class_instance = db.query(Class).filter(Class.id == assignment.class_id).first()
    if not class_instance:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if already assigned
    existing = db.query(TeacherClass).filter(
        TeacherClass.teacher_id == assignment.teacher_id,
        TeacherClass.class_id == assignment.class_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher is already assigned to this class")

    # Assign class to teacher
    new_assignment = TeacherClass(
        teacher_id=assignment.teacher_id,
        class_id=assignment.class_id
    )
    db.add(new_assignment)
    db.commit()

    return {"detail": "Class assigned to teacher successfully."}


@router.delete("/teacher-class-assignments/{teacher_id}/{class_id}", response_model=dict)
def remove_class_from_teacher(
    teacher_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)  # Allow both admin and teacher
):
    # Check if user is admin or teacher
    if user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # If the user is a teacher, ensure they can only remove themselves
    if user.role == "teacher" and teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Teachers can only remove themselves from classes")

    # Validate assignment
    existing = db.query(TeacherClass).filter(
        TeacherClass.teacher_id == teacher_id,
        TeacherClass.class_id == class_id
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Remove the assignment
    db.delete(existing)
    db.commit()
    return {"detail": "Class removed from teacher successfully."}
