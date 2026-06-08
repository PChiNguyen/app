from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from db.models.assessment_template import AssessmentType, Semester, Coefficient
from typing import Optional

class AssessmentTemplateCreate(BaseModel):
    subject_id: int
    name: str = Field(..., min_length=2, max_length=100, description="Tên bài kiểm tra (VD: 15 phút lần 1)")
    type: AssessmentType
    semester: Semester
    # 🚨 NO COEFFICIENT HERE! The backend auto-fills it safely.
    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Tên mẫu đánh giá không được để trống")
        if len(name.strip()) < 2:
            raise ValueError("Tên mẫu đánh giá phải có ít nhất 2 ký tự")
        return name.strip()
    @field_validator("semester")
    @classmethod
    def validate_semester(cls, semester):
        if isinstance(semester, Semester):
            return semester
        if isinstance(semester, int):
            try:
                return Semester(semester)
            except ValueError:
                raise ValueError(f"Học kỳ không hợp lệ. Vui lòng chọn từ: {[e.value for e in Semester]}")
        raise ValueError("Học kỳ phải là 1 hoặc 2")


class AssessmentTemplateUpdate(BaseModel):
    name: Optional[str] | None = Field(None, min_length=2, max_length=100, description="Tên bài kiểm tra (VD: 15 phút lần 1)")
    type: Optional[AssessmentType] | None = None
    semester: Optional[Semester] | None = None
    # 🚨 STILL NO COEFFICIENT! Updates can't change it either.

class AssessmentTemplateResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    type: AssessmentType
    semester: Semester
    coefficient: Coefficient 

    model_config = ConfigDict(from_attributes=True)