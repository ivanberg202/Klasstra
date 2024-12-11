from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile, Student, ParentStudent, Class
from app.schemas.users import UserCreate, UserUpdate, UserResponse, StudentCreate, StudentResponse
from app.routers.auth import get_current_user, role_required
import json
from app.schemas.users import UserResponse
from app.models import User, TeacherClass, ClassRepresentative
from app.schemas.users import UserResponse, UserProfileResponse

router = APIRouter()


from sqlalchemy.orm import joinedload

@router.get("/users/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Allow access only to admin or the user themselves
    if user.username != username and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    
    # Fetch the user with the profile eagerly loaded
    db_user = (
        db.query(User)
        .options(joinedload(User.profile))  # Eagerly load the profile relationship
        .filter(User.username == username)
        .first()
    )
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Use Pydantic's built-in serialization directly
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role,
        language=db_user.language,
        profile=db_user.profile and UserProfileResponse.model_construct(**db_user.profile.__dict__)
    )



@router.put("/users/{username}/update", response_model=UserResponse)
def update_user(username: str, user_update: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Allow access only to admin or the user themselves
    if user.username != username and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update User details
    user_data = user_update.dict(exclude_unset=True)
    profile_data = user_data.pop('profile', None)

    for key, value in user_data.items():
        setattr(db_user, key, value)

    # Update or create UserProfile
    if profile_data:
        students_data = profile_data.pop('students', None)

        # Remove any class or school-related fields
        profile_data.pop('class_id', None)
        profile_data.pop('school_id', None)

        if db_user.profile:
            for p_key, p_value in profile_data.items():
                setattr(db_user.profile, p_key, p_value)
        else:
            db_user.profile = UserProfile(user_id=db_user.id, **profile_data)
            db.add(db_user.profile)

        # Handle students if provided (for parents)
        if students_data:
            for student_info in students_data:
                # Create the student
                student = Student(
                    first_name=student_info.first_name,
                    last_name=student_info.last_name,
                    class_id=student_info.class_id
                )
                db.add(student)
                db.commit()
                db.refresh(student)

                # Associate the parent with the student
                parent_student = ParentStudent(
                    parent_id=db_user.id,
                    student_id=student.id
                )
                db.add(parent_student)
                db.commit()

    db.commit()
    db.refresh(db_user)
    return db_user



@router.post("/users/parent/add_child", response_model=StudentResponse)
def add_child(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    print("Received payload:", student_data)
    print("Current user:", user.id, user.role)

    if user.role != "parent":
        raise HTTPException(status_code=403, detail="Only parents can add children.")

    # Validate class_id
    class_instance = db.query(Class).filter(Class.id == student_data.class_id).first()
    if not class_instance:
        raise HTTPException(status_code=400, detail="Invalid class_id")

    # Check for duplicate student (same name and class)
    existing_student = (
        db.query(Student)
        .filter(
            Student.first_name == student_data.first_name,
            Student.last_name == student_data.last_name,
            Student.class_id == student_data.class_id,
        )
        .first()
    )
    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="A student with the same name is already enrolled in this class."
        )

    # Create the student
    new_student = Student(
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        class_id=student_data.class_id
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Associate the parent with the student
    parent_student = ParentStudent(
        parent_id=user.id,
        student_id=new_student.id
    )
    db.add(parent_student)
    db.commit()

    return new_student



@router.delete("/users/{username}/delete", response_model=dict)
def delete_user(username: str, db: Session = Depends(get_db), user: User = Depends(role_required("admin"))):
    # Fetch the user by username
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Delete associated profile
    if db_user.profile:
        db.delete(db_user.profile)

    # Delete associated students (via ParentStudent relationship)
    for association in db_user.children:
        student = association  # Directly access the student
        db.query(ParentStudent).filter(
            ParentStudent.parent_id == db_user.id, 
            ParentStudent.student_id == student.id
        ).delete()
        # Delete the student only if no other parents are associated
        if not db.query(ParentStudent).filter(ParentStudent.student_id == student.id).first():
            db.delete(student)

    # Finally, delete the user
    db.delete(db_user)
    db.commit()
    return {"detail": f"User {username} successfully deleted"}



@router.delete("/users/parent/delete_child/{student_id}", status_code=200)
def delete_child(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role not in ["parent", "admin"]:
        raise HTTPException(status_code=403, detail="Only parents and admins can delete children.")

    # Check if the student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Check if the student is associated with the parent
    parent_student = (
        db.query(ParentStudent)
        .filter(ParentStudent.parent_id == user.id, ParentStudent.student_id == student_id)
        .first()
    )
    if not parent_student:
        raise HTTPException(status_code=403, detail="This student is not associated with you.")

    # Delete the association
    db.delete(parent_student)

    # Optionally, delete the student record as well (if not referenced elsewhere)
    db.delete(student)

    # Commit the changes
    db.commit()

    return {"detail": "Student deleted successfully."}