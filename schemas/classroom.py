from pydantic import BaseModel, ConfigDict, Field 
from uuid import UUID
from typing import Optional    
   
class ClassroomBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description='Full name of the classroom')

class ClassroomCreate(ClassroomBase):
    pass 
class ClassroomUpdate(ClassroomBase):
    name: Optional[str]= Field(None, min_length=2, max_length=50,description="Update the classroom's name")
    teacher_id: Optional[UUID]= Field(None, description="Move classroom to a different teacher") 

class ClassroomRead(ClassroomBase):
    id: UUID

    model_config= ConfigDict(from_attributes=True)   

class StudentRankingRead(BaseModel):
    name: str
    gpa: float 
