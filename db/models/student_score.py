from sqlalchemy import Column, Integer, Float, String, ForeignKey, CheckConstraint, UUID as SQLUUID, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates  
from db.base import Base
from typing import TYPE_CHECKING
import uuid
import math 
from enum import Enum 
if TYPE_CHECKING:
    from db.models.student import Student
    from db.models.assessment_template import AssessmentTemplate
class Status(Enum):
    GRADED= "graded"
    PENDING= "pending"


class StudentScore(Base):
    __tablename__ = 'student_scores'

    id: Mapped[uuid.UUID] = mapped_column(SQLUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    student_id: Mapped[uuid.UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'))
    assessment_template_id: Mapped[int] = mapped_column(Integer, ForeignKey('assessment_templates.id', ondelete='CASCADE'))
    
    score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[Status] = mapped_column(SQLEnum(Status, length=20, native_enum=False), nullable=False, default=Status.PENDING)

    student: Mapped["Student"] = relationship('Student', back_populates='student_scores')
    assessment_template: Mapped["AssessmentTemplate"] = relationship('AssessmentTemplate', back_populates='scores')

    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 10', name='score_range_check'),
    )



#

    @validates('score')
    def validate_score(self, key, input_value):
        # 1. The Empty Slot Bypass
        if input_value is None:
            self.status = Status.PENDING  # 👈 AUTO-SET TO PENDING!
            return None

        # 2. The Boolean Trap
        if isinstance(input_value, bool):
            raise ValueError("Điểm số không được là giá trị Boolean (True/False)")

        # 3. The Strict Type Check
        if not isinstance(input_value, (int, float)):
            raise ValueError("Điểm số phải là một số")

        # 4. The Math Horrors
        if math.isnan(input_value) or math.isinf(input_value):
            raise ValueError("Điểm số không hợp lệ (Không được là NaN hoặc Vô cực)")

        # 5. The Range Check
        if input_value < 0 or input_value > 10:
            raise ValueError("Điểm số phải nằm trong khoảng từ 0 đến 10")

        # 6. The Clean Return
        self.status = Status.GRADED  # 👈 AUTO-SET TO GRADED!
        return round(float(input_value), 2)
    
    @validates('status')
    def validate_status(self, key, input_value: str):
        if isinstance(input_value, Status):
            return input_value
        if isinstance(input_value, str):
            try:
                return Status(input_value.lower())
            except ValueError:
                raise ValueError(f"'{input_value}' không phải là trạng thái hợp lệ. Vui lòng chọn từ: {[e.value for e in Status]}")
        raise ValueError("Trạng thái phải là một chuỗi hoặc một giá trị của Enum Status")
        #this final raise statement catches all the remaining edge cases, such as if someone tries to set status to an integer or a completely different type. It ensures that only valid inputs are accepted and provides clear error messages when invalid data is encountered.
    @validates('student_id')
    def validate_student_id(self, key, input_value):
        if not input_value:
            raise ValueError("student_id không được để trống")
        if not isinstance(input_value, uuid.UUID):
            raise ValueError("student_id phải là một UUID hợp lệ")
        return input_value
    @validates('assessment_template_id')
    def validate_assessment_template_id(self, key, input_value):
        if not input_value:
            raise ValueError("assessment_template_id không được để trống")
        if not isinstance(input_value, int):
            raise ValueError("assessment_template_id phải là một số nguyên hợp lệ")
        return input_value


    def __repr__(self) -> str:
        return f"StudentScore(id={self.id!r}, student_id={self.student_id!r}, assessment_template_id={self.assessment_template_id!r}, score={self.score!r}, status={self.status!r})"
       
 
