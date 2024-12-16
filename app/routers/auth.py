# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import secrets
from app.utils.utils import send_email

from app.database import get_db
from app.models import User, UserProfile, Class, Student, ParentStudent, ClassRepresentative
from app.schemas.users import (
    UserCreate,
    UserResponse,
    UserProfileCreate,
    UserProfileResponse,
    StudentCreate,
    teacher_classAssignment
)

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_key")  # Replace 'fallback_key' with a secure key
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = "HS256"

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Password Reset Token Model (For demonstration; use DB in production)
class PasswordResetToken(BaseModel):
    token: str
    expires_at: datetime

# In-memory store for reset tokens (Replace with persistent storage in production)
reset_tokens = {}  # key: user_id, value: PasswordResetToken

# Function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create JWT access tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to authenticate user credentials
def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    print(f"Query result for username '{username}': {user}")

    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

# Role-based access control decorator (supports multiple roles)
def role_required(allowed_roles: List[str]):
    def decorator(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{user.role}'."
            )
        return user
    return decorator

# Dependency to get the current authenticated user
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logger.error("JWT payload missing 'sub'")
            raise credentials_exception
        user_id = int(user_id_str)
        role = payload.get("role")
        if role is None:
            logger.error("JWT payload missing 'role'")
            raise credentials_exception
        token_data = {"user_id": user_id, "role": role}
    except (JWTError, ValueError) as e:
        logger.error(f"Error decoding JWT: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error(f"User with ID {user_id} not found")
        raise credentials_exception
    return user


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check for existing user
    existing_user = (
        db.query(User)
        .filter((User.username == user_data.username) | (User.email == user_data.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username or email already exists."
        )

    try:
        # Hash the user's password
        hashed_password = hash_password(user_data.password)
        
        # Create the new user without optional fields
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            role=user_data.role,
        )
        db.add(new_user)
        
        # Flush to assign an ID to new_user
        db.flush()
        
        # Commit the new user to the database
        db.commit()
        db.refresh(new_user)

    except IntegrityError as e:
        db.rollback()
        logger.exception(f"Integrity error for user: {user_data.username} - {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error occurred during registration. Possibly a duplicate entry."
        ) from e
    except Exception as e:
        db.rollback()
        logger.exception(f"Unexpected error during registration for user: {user_data.username} - {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        ) from e

    # Fetch the user for the response
    db_user = (
        db.query(User)
        .filter(User.id == new_user.id)
        .first()
    )

    return UserResponse.from_orm(db_user)


@router.post("/auth/reset-password", response_model=dict, status_code=status.HTTP_200_OK)
def reset_password(email: str, token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Reset a user's password.
    - **email**: User's email address.
    - **token**: Reset token sent to the user's email.
    - **new_password**: New password to set.
    """
    # Fetch the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Validate the reset token
    reset_token = reset_tokens.get(user.id)
    if not reset_token or reset_token.token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token."
        )
    
    if datetime.utcnow() > reset_token.expires_at:
        del reset_tokens[user.id]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired."
        )

    # Update the user's password
    user.password = hash_password(new_password)
    db.commit()

    # Remove the token after successful reset
    del reset_tokens[user.id]

    return {"message": "Password updated successfully."}



# Endpoint for user login and token generation
@router.post("/token", response_model=dict)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return a JWT access token.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch first_name from the user's profile
    first_name = user.profile.first_name if user.profile else "User"
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



# Function to generate a secure reset token
def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)



@router.post("/auth/request-password-reset", response_model=dict, status_code=status.HTTP_200_OK)
def request_password_reset(email: str, db: Session = Depends(get_db)):
    """
    Request a password reset. Sends a reset token to the user's email.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Generate a secure reset token
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    reset_tokens[user.id] = PasswordResetToken(token=token, expires_at=expires_at)

    # Send the reset token via email
    reset_link = f"https://yourdomain.com/reset-password?email={email}&token={token}"
    try:
        send_email(
            to_email=user.email,
            subject="Password Reset Request",
            body=f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nThis link will expire in 1 hour.\n\nIf you did not request a password reset, please ignore this email."
        )
    except Exception as e:
        # In production, handle email sending errors appropriately
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send reset email.")

    return {"message": "Password reset link has been sent to your email."}
