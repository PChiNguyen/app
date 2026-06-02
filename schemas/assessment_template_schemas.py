from pydantic import BaseModel, ConfigDict, Field
from db.models.assessment_template import AssessmentType, Semester, Coefficient

class AssessmentTemplateCreate(BaseModel):
    subject_id: int
    name: str = Field(..., min_length=2, max_length=100, description="Tên bài kiểm tra (VD: 15 phút lần 1)")
    type: AssessmentType
    semester: Semester
    # 🚨 NO COEFFICIENT HERE! The backend auto-fills it safely.


class AssessmentTemplateResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    type: AssessmentType
    semester: Semester
    coefficient: Coefficient 

    model_config = ConfigDict(from_attributes=True)