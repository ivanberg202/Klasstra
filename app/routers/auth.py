from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile, School, Class, Student, ParentStudent, ClassRepresentative
from app.schemas.users import UserCreate, UserProfileResponse, UserResponse, StudentCreate
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import secrets
from app.utils import send_email  # A utility function for sending emails
from sqlalchemy.orm import joinedload

router = APIRouter()

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

reset_tokens = {}  # In-memory store for reset tokens (replace with DB in production)

# OAuth2PasswordBearer setup with the correct token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Load environment variables from .env
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
ALGORITHM = "HS256"


# Function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to create JWT access tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode["first_name"] = data.get("first_name")  # Include first_name in token

    # Ensure 'sub' is a string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Function to authenticate user credentials
def authenticate_user(username: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        return None
    return user


@router.post("/auth/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check for existing user
    existing_user = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username or email already exists."
        )

    # Create the new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role,
        language=user_data.language,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create the profile if provided (but do not handle class logic here)
    profile = None
    if user_data.profile:
        profile_data = user_data.profile.dict(exclude_unset=True)
        students_data = profile_data.pop('students', None)

        # Remove any class or school related fields from profile_data if present
        profile_data.pop('school_id', None)
        profile_data.pop('class_id', None)

        # Create the UserProfile
        profile = UserProfile(user_id=new_user.id, **profile_data)
        db.add(profile)
        db.commit()

        # Handle students if provided (this is about adding children, not assigning classes to the user)
        if students_data:
            for student_info in students_data:
                # Check for duplicate student in the same class
                existing_student = db.query(Student).filter(
                    Student.first_name == student_info['first_name'],
                    Student.last_name == student_info['last_name'],
                    Student.class_id == student_info['class_id']
                ).first()
                if existing_student:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Student {student_info['first_name']} {student_info['last_name']} "
                               f"already exists in class {student_info['class_id']}."
                    )

                # Create the student
                student = Student(
                    first_name=student_info['first_name'],
                    last_name=student_info['last_name'],
                    class_id=student_info['class_id']
                )
                db.add(student)
                db.commit()
                db.refresh(student)

                # Associate parent and student
                parent_student = ParentStudent(
                    parent_id=new_user.id,
                    student_id=student.id
                )
                db.add(parent_student)
                db.commit()

    # No call to sync_role_specific_relationships here, since class assignment is handled elsewhere now.

    # Fetch the user with the profile for the response
    db_user = (
        db.query(User)
        .options(joinedload(User.profile))
        .filter(User.id == new_user.id)
        .first()
    )

    return UserResponse.model_validate(db_user)



@router.post("/auth/reset-password")
def reset_password(email: str, token: str, new_password: str, db: Session = Depends(get_db)):
    # Fetch the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Validate the reset token
    if reset_tokens.get(user.id) != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token."
        )

    # Update the user's password
    user.password = hash_password(new_password)
    db.commit()

    # Remove the token after successful reset
    del reset_tokens[user.id]

    return {"message": "Password updated successfully."}




# Endpoint for user login and token generation
@router.post("/token", include_in_schema=True)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Include first_name from the user's profile
    first_name = user.profile.first_name if user.profile else "User"
    
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role, "first_name": first_name}
    )
    return {"access_token": access_token, "token_type": "bearer"}



# Function to retrieve user from JWT token
def get_user_from_token(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user_role = payload.get("role")
        if user_id is None or user_role is None:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            user.role = user_role  # Assign the role from the token to the user object
        return user
    except JWTError:
        return None

# Dependency to get the current authenticated user
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user_role = payload.get("role")
        if user_id is None or user_role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            user.role = user_role  # Assign the role from the token to the user object
        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# Role-based access control decorator
def role_required(required_role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required {required_role} role"
            )
        return user
    return role_checker


