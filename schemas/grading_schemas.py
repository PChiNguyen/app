from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class SubjectAverageRead(BaseModel):
    student_id: UUID
    student_name: str
    subject_id: int
    sub_avg: Optional[float] = None  # Can be None if tests are incomplete!
    completed_tests: int
    required_tests: int

    model_config = ConfigDict(from_attributes=True)

class SemesterGPARead(BaseModel):
    student_id: UUID
    student_name: str
    semester_gpa: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class YearlySubjectAverageRead(BaseModel):
    student_id: UUID
    student_name: str
    subject_id: int
    yearly_sub_avg: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class YearlyGPARead(BaseModel):
    student_id: UUID
    student_name: str
    yearly_gpa: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)