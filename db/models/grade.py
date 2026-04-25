import uuid
import re
import enum
from sqlalchemy import String, Float, ForeignKey, CheckConstraint, Enum as SQLEnum, UUID          

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from db.base import Base

class SubjectCoefficient(int, enum.Enum):
    TESTS = 1
    MIDTERM = 2
    FINAL = 3

class Grade(Base):
    __tablename__ = 'grades'    
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('students.id', ondelete='CASCADE'),
        nullable=False
    )
                                                
    subject: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    
    coefficient: Mapped[SubjectCoefficient] = mapped_column(
        SQLEnum(SubjectCoefficient),
        nullable=False,
        default=SubjectCoefficient.TESTS
    )

    student = relationship("Student", back_populates="grades")

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 10", name='score_range_check'),
        # Notice I deleted the DB-level regex constraint.
    )   
    
    @validates('subject')
    def validate_subject(self, key, input_value: str):
        if not input_value or not input_value.strip():
            raise ValueError("Môn học không được để trống")
        
        # Temporarily remove spaces to check the characters
        subject_no_spaces = input_value.replace(" ", "")
        
        # .isalnum() perfectly allows 'Vật lý 10' but blocks 'Vật lý @#'
        if not subject_no_spaces.isalnum():
            raise ValueError("Môn học chỉ được chứa chữ cái, số và khoảng trắng")
            
        return input_value.strip()

    @validates('score')
    def validate_score(self, key, input_value: float):
        if input_value is None: # FIX: Allows 0.0 to pass!
            raise ValueError("Điểm số không được để trống")
        if not isinstance(input_value, (float, int)): # Allow int just in case they type '8' instead of '8.0'
            raise ValueError("Điểm số phải là một số thực")
        if input_value < 0 or input_value > 10:
            raise ValueError("Điểm phải nằm trong khoảng từ 0 đến 10")
        return float(input_value)

    @validates('coefficient') # FIX: Changed from 'role' to 'coefficient'
    def validate_coefficient(self, key, input_value):
        if isinstance(input_value, SubjectCoefficient):
            return input_value
        if isinstance(input_value, int):
            try:
                return SubjectCoefficient(input_value)
            except ValueError:
                raise ValueError(f"Hệ số không hợp lệ. Phải là 1, 2, hoặc 3.")
        raise ValueError("Hệ số phải là số nguyên (1, 2, 3)")

    @validates('student_id')
    def validate_student_id(self, key, input_value):
        if not input_value:
            raise ValueError("student_id không được để trống")
        if not isinstance(input_value, uuid.UUID):
            raise ValueError("student_id phải là một UUID hợp lệ")
        return input_value