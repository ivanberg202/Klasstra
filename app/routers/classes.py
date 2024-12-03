from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Class
from app.schemas.classes import ClassCreate, ClassResponse

router = APIRouter()

@router.post("/classes/create", response_model=ClassResponse)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    new_class = Class(
        name=class_data.name,
        school_id=class_data.school_id
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class
