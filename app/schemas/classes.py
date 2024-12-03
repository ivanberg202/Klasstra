from pydantic import BaseModel, ConfigDict

class ClassBase(BaseModel):
    name: str
    school_id: int

class ClassCreate(ClassBase):
    pass  # No additional fields for creation

class ClassResponse(ClassBase):
    id: int  # Include the ID for responses

    model_config = ConfigDict(from_attributes=True)  # Replaces orm_mode
