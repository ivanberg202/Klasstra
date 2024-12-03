from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import School
from app.schemas.schools import SchoolCreate, SchoolResponse

router = APIRouter()

@router.post("/schools/create", response_model=SchoolResponse)
def create_school(school_data: SchoolCreate, db: Session = Depends(get_db)):
    # Check if a school with the same name already exists
    existing_school = db.query(School).filter(School.name == school_data.name).first()
    if existing_school:
        raise HTTPException(status_code=400, detail="School with this name already exists")

    # Create the new school
    new_school = School(name=school_data.name)
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    return new_school
