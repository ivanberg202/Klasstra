from fastapi import FastAPI
from app.database import Base, engine
from app.models import User, School, Class, Student, ParentStudent, TeacherClass, ClassRepresentative, Announcement
from app.routers import auth, announcements, classes, schools, users, dashboards
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import logging
from app.database import Base, engine


app = FastAPI()


# Create database tables
Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(announcements.router, tags=["Announcements"])
app.include_router(classes.router, tags=["Classes"])
app.include_router(schools.router, tags=["Schools"])
app.include_router(users.router, tags=["Users"])
app.include_router(dashboards.router, tags=["Dashboards"])
