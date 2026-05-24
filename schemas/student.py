from pydantic import BaseModel, ConfigDict, Field 
from uuid import UUID
from typing import Optional   

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description='Full name of the student')
    classroom_id: UUID = Field(..., description='Classroom ID')
class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel): # We don't inherit here to avoid 'Required' conflicts
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=50, 
        description="Update the student's name"
    )
    classroom_id: Optional[UUID] = Field(
        None, 
        description="Move student to a different classroom"
    )
class StudentRead(StudentBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True) 

class ReportCardDTO(BaseModel):
    student_id: UUID
    student_name: str
    gpa: float
    class_rank: int
    model_config = ConfigDict(from_attributes=True)


