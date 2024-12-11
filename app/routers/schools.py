from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import School
from app.schemas.schools import SchoolCreate, SchoolResponse
from app.routers.auth import role_required

router = APIRouter()


@router.post("/schools/create", response_model=SchoolResponse, dependencies=[Depends(role_required("admin"))])
def create_school(school_data: SchoolCreate, db: Session = Depends(get_db)):
    existing_school = db.query(School).filter(School.name == school_data.name).first()
    if existing_school:
        raise HTTPException(status_code=400, detail="School already exists")
    new_school = School(name=school_data.name)
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    return new_school


@router.get("/schools/all", response_model=List[SchoolResponse])
def get_all_schools(db: Session = Depends(get_db)):
    schools = db.query(School).all()
    return schools


@router.get("/schools/{school_id}", response_model=SchoolResponse, dependencies=[Depends(role_required("admin"))])
def get_school(school_id: int, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.put("/schools/{school_id}/update", response_model=SchoolResponse, dependencies=[Depends(role_required("admin"))])
def update_school(school_id: int, school_data: SchoolCreate, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    school.name = school_data.name
    db.commit()
    db.refresh(school)
    return school


@router.delete("/schools/{school_id}", dependencies=[Depends(role_required("admin"))])
def delete_school(school_id: int, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    db.delete(school)
    db.commit()
    return {"message": "School deleted successfully"}
