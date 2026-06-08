import re

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from uuid import UUID
from typing import Optional    
def check_classroom_name_rules(name: str) -> str:
    if not name.strip():
        raise ValueError("Tên lớp học không được để trống hoặc chỉ có khoảng trắng")
    if not isinstance(name, str):
        raise ValueError("Tên lớp học phải là một chuỗi")
    if not re.match(r'^[a-zA-Z\s]+$', name):
        raise ValueError("Tên lớp học chỉ được chứa chữ cái và khoảng trắng")
    if len(name.strip()) < 2:
        raise ValueError("Tên lớp học phải có ít nhất 2 ký tự")
    
    return name.strip()
   
class ClassroomBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description='Full name of the classroom')

    @field_validator('name')
    @classmethod
    def validate_name(cls, name: str) -> str:
        return check_classroom_name_rules(name)



class ClassroomCreate(ClassroomBase):
    teacher_id: UUID = Field(..., description="UUID of the teacher assigned to this classroom")
class ClassroomUpdate(ClassroomBase):
    name: Optional[str]= Field(None, min_length=2, max_length=50,description="Update the classroom's name")
    teacher_id: Optional[UUID]= Field(None, description="Move classroom to a different teacher") 
    @field_validator('name')
    @classmethod
    def validate_optional_name(cls, name: Optional[str]) -> Optional[str]:
        if name is None:
            return None
        return check_classroom_name_rules(name)

class ClassroomRead(ClassroomBase):
    id: UUID

    model_config= ConfigDict(from_attributes=True)   

class StudentRankingRead(BaseModel):
    name: str 
    gpa: float 
