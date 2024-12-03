from pydantic import BaseModel, ConfigDict

class SchoolBase(BaseModel):
    name: str

class SchoolCreate(SchoolBase):
    pass

class SchoolResponse(SchoolBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
