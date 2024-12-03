from fastapi import FastAPI
from app.database import Base, engine
from app.models import User, School, Class, Student, ParentStudent, TeacherClass, ClassRepresentative, Announcement
from app.routers import auth, announcements
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Klasstra API",
        version="1.0.0",
        description="API for the Klasstra application",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token",
                    "scopes": {},
                }
            },
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Create database tables
Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(announcements.router, tags=["Announcements"])


# Example route to test the app
@app.get("/")
async def read_root():
    return {"message": "Hello, Klasstra!"}

