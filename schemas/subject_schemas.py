from pydantic import BaseModel, ConfigDict
from db.models.subject import SubName

class SubjectResponse(BaseModel):
    id: int
    name: SubName
    # This tells Pydantic: "It is okay to read data directly from the SQLAlchemy Subject model"
    model_config = ConfigDict(from_attributes=True)