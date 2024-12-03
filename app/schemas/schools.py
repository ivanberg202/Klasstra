from pydantic import BaseModel, ConfigDict

class SchoolBase(BaseModel):
    name: str  # Name of the school

class SchoolCreate(SchoolBase):
    pass  # No additional fields needed for creation

class SchoolResponse(SchoolBase):
    id: int  # Include the ID for responses

    model_config = ConfigDict(from_attributes=True)  # Replaces orm_mode
