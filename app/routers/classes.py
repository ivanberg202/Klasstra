# classes.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List

from app.database import get_db
from app.models import Class, User, teacher_class, Student, ParentStudent, ClassRepresentative, School
from app.schemas.classes import ClassCreate, ClassResponse, ClassAssignmentRequest
from app.schemas.users import teacher_classAssignment
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
            .join(teacher_class, teacher_class.c.class_id == Class.id)
            .filter(teacher_class.c.teacher_id == user.id)
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
        assignment = db.query(teacher_class).filter(
            teacher_class.c.teacher_id == current_user.id,  # Corrected to use .c
            teacher_class.c.class_id == class_id
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
        assignment = db.query(teacher_class).filter(
            teacher_class.c.teacher_id == current_user.id,  # Corrected to use .c
            teacher_class.c.class_id == class_id
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
        assignment = db.query(teacher_class).filter(
            teacher_class.c.teacher_id == current_user.id,  # Corrected to use .c
            teacher_class.c.class_id == class_id
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

    # If Admin is assigning to another user, the request should include `user_id`
    # Assuming `ClassAssignmentRequest` includes `user_id` when role is admin
    # Modify accordingly if not

    # For simplicity, here we assume teachers can only assign themselves
    # Admins can assign to any user by providing `user_id` in the request
    if current_user.role == "admin":
        if hasattr(request, 'user_id') and request.user_id:
            user_id = request.user_id
        else:
            raise HTTPException(status_code=400, detail="Admin must provide `user_id` to assign class")

    # Check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the class exists
    class_instance = db.query(Class).filter(Class.id == class_id).first()
    if not class_instance:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if the assignment already exists
    existing = db.query(teacher_class).filter(
        teacher_class.c.teacher_id == user_id,  # Corrected to use .c
        teacher_class.c.class_id == class_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Class is already assigned to the user")

    # Create the new assignment
    insert_stmt = teacher_class.insert().values(
        teacher_id=user_id,
        class_id=class_id,
    )
    db.execute(insert_stmt)
    db.commit()

    return {"detail": "Class assigned to user successfully."}


@router.get("/teacher-classes", response_model=List[ClassResponse])
def get_teacher_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all classes assigned to the logged-in teacher.
    """
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Base query: Join Class and School
    query = db.query(
        Class.id.label("id"),
        Class.name.label("class_name"),
        Class.school_id.label("school_id"),
        School.name.label("school_name")
    ).join(School, Class.school_id == School.id)

    if current_user.role == "teacher":
        # Join with teacher_class to filter classes assigned to the current teacher
        query = query.join(teacher_class, teacher_class.c.class_id == Class.id)\
                     .filter(teacher_class.c.teacher_id == current_user.id)

    classes = query.all()

    return classes


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

    # If Admin is removing assignment from another user, handle accordingly
    # Assuming only teachers can remove their own assignments in this endpoint
    # Modify if admins need to remove assignments from others

    # Check if the assignment exists
    existing = db.query(teacher_class).filter(
        teacher_class.c.teacher_id == user_id,  # Corrected to use .c
        teacher_class.c.class_id == class_id
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Remove the assignment
    delete_stmt = teacher_class.delete().where(
        teacher_class.c.teacher_id == user_id,
        teacher_class.c.class_id == class_id
    )
    db.execute(delete_stmt)
    db.commit()

    return {"detail": "Class removed from user successfully."}
