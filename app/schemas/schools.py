from pydantic import BaseModel, ConfigDict

class SchoolBase(BaseModel):
    name: str

class SchoolCreate(SchoolBase):
    pass

class SchoolResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
