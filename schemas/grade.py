from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from db.models.grade import SubjectCoefficient, SubjectName  # Import the VIP list!

# 1. The Core Attributes (Shared by almost everything)
class GradeBase(BaseModel):
    subject: SubjectName = Field(..., description="Tên môn học, phải là một trong các giá trị: Math, Physics, Chemistry, Literature, English")
    score: float = Field(..., ge=0.0, le=10.0) 
    coefficient: SubjectCoefficient = Field(default=SubjectCoefficient.TESTS)

# 2. What we expect from the Teacher (POST request)
class GradeCreate(GradeBase):
    student_id: UUID

# 3. What we return to the Frontend (GET request)
class GradeRead(GradeBase):
    id: UUID
    student_id: UUID

    # This tells Pydantic to read SQLAlchemy ORM objects perfectly
    model_config = ConfigDict(from_attributes=True) 

# 4. What we expect for Edits (PUT/PATCH request)
# Everything is Optional because they might only want to update the score
class GradeUpdate(BaseModel):
    subject: Optional[SubjectName] = Field(default=None, description="Tên môn học, phải là một trong các giá trị: Math, Physics, Chemistry, Literature, English")
    score: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    coefficient: Optional[SubjectCoefficient] = Field(default=None)