from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserProfile
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.routers.auth import get_current_user, role_required
import json
from app.schemas.users import UserResponse
from app.models import User
from app.schemas.users import UserResponse, UserProfileResponse


router = APIRouter()


@router.get("/users/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Allow access only to admin or the user themselves
    if user.username != username and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Use Pydantic's built-in serialization directly
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        role=db_user.role,
        language=db_user.language,
        profile=db_user.profile and UserProfileResponse.from_orm(db_user.profile)
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
    for key, value in user_update.dict(exclude_unset=True).items():
        if key in ["email", "role", "language"]:
            setattr(db_user, key, value)
    
    # Update UserProfile details
    if db_user.profile:
        for key, value in user_update.dict(exclude_unset=True).items():
            if key in ["first_name", "last_name", "phone_number", "address", "hobbies", "preferred_contact_method"]:
                setattr(db_user.profile, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user



@router.delete("/users/{username}/delete", response_model=dict)
def delete_user(username: str, db: Session = Depends(get_db), user: User = Depends(role_required("admin"))):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": f"User {username} successfully deleted"}
