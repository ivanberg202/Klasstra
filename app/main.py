from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.models import User, School, Class, Student, ParentStudent, TeacherClass, ClassRepresentative, Announcement
from app.routers import auth, announcements, classes, schools, users, dashboards
import os

# Initialize the FastAPI app
app = FastAPI()

# Mount static directory for serving custom assets (e.g., custom CSS)
static_directory = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_directory), name="static")

# Add CORS middleware
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(announcements.router, tags=["Announcements"])
app.include_router(classes.router, tags=["Classes"])
app.include_router(schools.router, tags=["Schools"])
app.include_router(users.router, tags=["Users"])
app.include_router(dashboards.router, tags=["Dashboards"])
