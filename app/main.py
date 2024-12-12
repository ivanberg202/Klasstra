from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.models import User, School, Class, Student, ParentStudent, TeacherClass, ClassRepresentative, Announcement
from app.routers import auth, announcements, classes, schools, users, dashboards
import os
import logging



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger(__name__)


# Initialize the FastAPI app
app = FastAPI()

# Resolve the static directory path
static_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
if not os.path.exists(static_directory):
    print(f"Warning: Static directory {static_directory} does not exist.")
app.mount("/static", StaticFiles(directory=static_directory), name="static")

# Add CORS middleware
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]  # Development frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Replace with ["*"] temporarily if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
except Exception as e:
    print(f"Error creating database tables: {e}")

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(announcements.router, tags=["Announcements"])
app.include_router(classes.router, tags=["Classes"])
app.include_router(schools.router, tags=["Schools"])
app.include_router(users.router, tags=["Users"])
app.include_router(dashboards.router, tags=["Dashboards"])
