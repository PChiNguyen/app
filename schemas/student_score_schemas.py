
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from db.models.student_score import Status

class StudentScoreCreate(BaseModel):
    student_id: UUID
    assessment_template_id: int
    # Optional because a teacher might create the roster before grading the papers
    score: Optional[float] = Field(default=None, ge=0, le=10, description="Điểm số từ 0 đến 10")

class StudentScoreUpdate(BaseModel):
    # When updating a score, you shouldn't be able to change the student or the test!
    # You ONLY update the number itself.
    score: Optional[float] = Field(default=None, ge=0, le=10, description="Điểm số từ 0 đến 10")

class StudentScoreResponse(BaseModel):
    id: UUID
    student_id: UUID
    assessment_template_id: int
    score: Optional[float]
    status: Status

    model_config = ConfigDict(from_attributes=True)