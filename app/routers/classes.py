from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Class
from app.schemas.classes import ClassCreate, ClassResponse
from app.routers.auth import role_required

router = APIRouter()

@router.post("/classes/create", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    existing_class = db.query(Class).filter(Class.name == class_data.name, Class.school_id == class_data.school_id).first()
    if existing_class:
        raise HTTPException(status_code=400, detail="Class already exists in this school")
    new_class = Class(name=class_data.name, school_id=class_data.school_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@router.get("/classes/{class_id}", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def get_class(class_id: int, db: Session = Depends(get_db)):
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_


@router.put("/classes/{class_id}/update", response_model=ClassResponse, dependencies=[Depends(role_required("admin"))])
def update_class(class_id: int, class_data: ClassCreate, db: Session = Depends(get_db)):
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    class_.name = class_data.name
    class_.school_id = class_data.school_id
    db.commit()
    db.refresh(class_)
    return class_


@router.delete("/classes/{class_id}", dependencies=[Depends(role_required("admin"))])
def delete_class(class_id: int, db: Session = Depends(get_db)):
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(class_)
    db.commit()
    return {"message": "Class deleted successfully"}
