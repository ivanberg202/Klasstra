from pydantic import BaseModel, ConfigDict

class ClassBase(BaseModel):
    name: str
    school_id: int

class ClassCreate(ClassBase):
    pass

class ClassResponse(ClassBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
