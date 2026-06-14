import re

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from uuid import UUID
from typing import Optional   
def check_student_name_rules(name: str) -> str:
    if not name or not name.strip():
            raise ValueError("Tên không được để trống")
        
        # Remove spaces temporarily just to check the letters
    name_no_spaces = name.replace(" ", "")
    # .isalpha() automatically allows 'Thảo Nguyên' but blocks 'Nguyên 123' or 'Nguyên!'
    if not name_no_spaces.isalpha():
        raise ValueError("Tên học sinh chỉ được chứa chữ cái và khoảng trắng")
    if len(name.strip()) < 2:
        raise ValueError("Tên học sinh phải có ít nhất 2 ký tự")
        
    return name.strip()
    

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description='Full name of the student')
    classroom_id: UUID = Field(..., description='Classroom ID')

    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        return check_student_name_rules(name)

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
    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        if name is None:
            return None
        return check_student_name_rules(name)

class StudentRead(StudentBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True) 

class ReportCardDTO(BaseModel):
    student_id: UUID
    student_name: str
    gpa: float
    class_rank: int

    
    model_config = ConfigDict(from_attributes=True)


