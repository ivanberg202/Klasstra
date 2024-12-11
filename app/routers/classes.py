# classes.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models import Class, User, TeacherClass, Student, ParentStudent, ClassRepresentative, School
from app.schemas.classes import ClassCreate, ClassResponse, ClassAssignmentRequest
from app.schemas.users import TeacherClassAssignment
from app.routers.auth import role_required, get_current_user

router = APIRouter()


@router.get('/classes/unrestricted', response_model=List[ClassResponse])
def get_unrestricted_classes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve all classes without any restrictions.
    - This endpoint is intended for dropdowns or general-purpose use cases.
    - Access is limited to authenticated users.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access this resource."
        )

    classes = (
        db.query(Class)
        .options(joinedload(Class.school))  # Include related school data
        .all()
    )

    return [
        {
            "id": cls.id,
            "class_name": cls.name,
            "school_id": cls.school_id,
            "school_name": cls.school.name,
        }
        for cls in classes
    ]



@router.get('/classes/all', response_model=List[ClassResponse])
def get_all_classes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve classes based on the user's role.
    - Admins: All classes across all schools.
    - Teachers: Only classes they are assigned to.
    - Parents: Only classes their children are enrolled in.
    - Class Representatives: Only classes they represent.
    """
    if user.role == 'admin':
        # Admins can see all classes
        classes = (
            db.query(Class)
            .options(joinedload(Class.school))
            .all()
        )
    elif user.role == 'teacher':
        # Teachers see only classes they are assigned to
        classes = (
            db.query(Class)
            .join(TeacherClass, TeacherClass.class_id == Class.id)
            .filter(TeacherClass.teacher_id == user.id)
            .options(joinedload(Class.school))
            .all()
        )
    elif user.role == 'parent':
        # Parents see classes their children are enrolled in
        classes = (
            db.query(Class)
            .join(Student, Student.class_id == Class.id)
            .join(ParentStudent, ParentStudent.student_id == Student.id)
            .filter(ParentStudent.parent_id == user.id)
            .options(joinedload(Class.school))
            .all()
        )
    elif user.role == 'class_representative':
        # Class Representatives see only classes they represent
        classes = (
            db.query(Class)
            .join(ClassRepresentative, ClassRepresentative.class_id == Class.id)
            .filter(ClassRepresentative.parent_id == user.id)
            .options(joinedload(Class.school))
            .all()
        )
    else:
        # For other roles, restrict access or return an empty list
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    
    # Transform results to match the expected response schema
    return [
        {
            "id": cls.id,
            "class_name": cls.name,
            "school_id": cls.school_id,
            "school_name": cls.school.name,
        }
        for cls in classes
    ]


@router.post("/classes/create", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def create_class(class_data: ClassCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new class.
    - Admins: Can create classes in any school.
    """
    # Check if class already exists in the school
    existing_class = db.query(Class).filter(Class.name == class_data.name, Class.school_id == class_data.school_id).first()
    if existing_class:
        raise HTTPException(status_code=400, detail="Class already exists in this school")
    
    # Create the new class
    new_class = Class(name=class_data.name, school_id=class_data.school_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return {
        "id": new_class.id,
        "class_name": new_class.name,
        "school_id": new_class.school_id,
        "school_name": new_class.school.name
    }


@router.get("/classes/{class_id}", response_model=ClassResponse, dependencies=[Depends(role_required(["admin", "teacher"]))])
def get_class(class_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve detailed information about a specific class.
    - Admins: Can access any class.
    - Teachers: Can access only classes they are assigned to.
    """
    # Fetch the class with the associated school
    class_instance = (
        db.query(Class)
        .options(joinedload(Class.school))
        .filter(Class.id == class_id)
        .first()
    )
    
    if not class_instance:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # If user is a teacher, verify assignment
    if current_user.role == 'teacher':
        assignment = db.query(TeacherClass).filter(
            TeacherClass.teacher_id == current_user.id,
            TeacherClass.class_id == class_id
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="You do not have access to this class")
    
    return {
        "id": class_instance.id,
        "class_name": class_instance.name,
        "school_id": class_instance.school_id,
        "school_name": class_instance.school.name,
    }


@router.put("/classes/{class_id}/update", response_model=ClassResponse, dependencies=[Depends(role_required(["admin", "teacher"]))])
def update_class(class_id: int, class_data: ClassCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update an existing class.
    - Admins: Can update any class.
    - Teachers: Can update only classes they are assigned to.
    """
    class_instance = db.query(Class).filter(Class.id == class_id).first()
    if not class_instance:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # If user is a teacher, verify assignment
    if current_user.role == 'teacher':
        assignment = db.query(TeacherClass).filter(
            TeacherClass.teacher_id == current_user.id,
            TeacherClass.class_id == class_id
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="You do not have permission to update this class")
    
    # Check for duplicate class name within the same school
    if db.query(Class).filter(Class.name == class_data.name, Class.school_id == class_data.school_id, Class.id != class_id).first():
        raise HTTPException(status_code=400, detail="Another class with this name already exists in the selected school")
    
    # Update class details
    class_instance.name = class_data.name
    class_instance.school_id = class_data.school_id
    db.commit()
    db.refresh(class_instance)
    
    return {
        "id": class_instance.id,
        "class_name": class_instance.name,
        "school_id": class_instance.school_id,
        "school_name": class_instance.school.name,
    }


@router.delete("/classes/{class_id}", dependencies=[Depends(role_required(["admin", "teacher"]))])
def delete_class(class_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a class.
    - Admins: Can delete any class.
    - Teachers: Can delete only classes they are assigned to.
    """
    class_instance = db.query(Class).filter(Class.id == class_id).first()
    if not class_instance:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # If user is a teacher, verify assignment
    if current_user.role == 'teacher':
        assignment = db.query(TeacherClass).filter(
            TeacherClass.teacher_id == current_user.id,
            TeacherClass.class_id == class_id
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this class")
    
    # Delete the class
    db.delete(class_instance)
    db.commit()
    
    return {"message": "Class deleted successfully"}



@router.post("/teacher-class-assignments", response_model=dict)
def assign_class_to_user(
    request: ClassAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    class_id = request.class_id
    
    """
    Assign a class to a user.
    - Admins: Can assign any user to any class by overriding `current_user`.
    - Teachers (users with the teacher role): Can assign themselves to classes.
    """
    user_id = current_user.id  # Use the logged-in user's ID

    # Validate role and permissions
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Check if the assignment already exists
    existing = db.query(TeacherClass).filter(
        TeacherClass.teacher_id == user_id,  # Use user_id here
        TeacherClass.class_id == class_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Class is already assigned to the user")

    # Create the new assignment
    new_assignment = TeacherClass(teacher_id=user_id, class_id=class_id)
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return {"detail": "Class assigned to user successfully."}



@router.delete("/teacher-class-assignments/{class_id}", response_model=dict)
def remove_class_assignment(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a class assignment from the current user (teacher).
    """
    user_id = current_user.id

    # Validate role and permissions
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Check if the assignment exists
    existing = db.query(TeacherClass).filter(
        TeacherClass.teacher_id == user_id,
        TeacherClass.class_id == class_id
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Remove the assignment
    db.delete(existing)
    db.commit()

    return {"detail": "Class removed from user successfully."}