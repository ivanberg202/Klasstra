from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile
from app.schemas.users import UserCreate, UserProfileResponse
from app.schemas.auth import UserResponse
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import secrets
from app.utils import send_email  # A utility function for sending emails

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
    # Ensure this line is present for schema validation
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role,
        language=user_data.language,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if user_data.profile:
        user_profile = UserProfile(
            user_id=new_user.id,
            **user_data.profile.dict()  # Ensure this references the nested profile schema
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        language=new_user.language,
        profile=user_profile and UserProfileResponse.from_orm(user_profile),
    )



@router.post("/auth/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email."
        )
    
    # Generate a secure reset token
    reset_token = secrets.token_urlsafe(32)
    reset_tokens[user.id] = reset_token

    # Send email (implement `send_email` in utils)
    send_email(
        to_email=user.email,
        subject="Password Reset",
        body=f"Use this token to reset your password: {reset_token}"
    )

    return {"message": "Password reset token sent to your email."}


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
@router.post("/token")
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
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role}
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