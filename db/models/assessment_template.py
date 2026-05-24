# db/models/assessment_template.py
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from enum import Enum, IntEnum
from db.base import Base

# The TYPE_CHECKING trick prevents the Circular Import Crash!
if TYPE_CHECKING:
    from db.models.subject import Subject
    from db.models.student_score import StudentScore

class AssessmentType(str, Enum):
    TEST = "test"        # Miệng, 15 phút, Thực hành
    MIDTERM = "midterm"  # Giữa kỳ / 1 tiết
    FINAL = "final"      # Cuối kỳ

class Coefficient(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3

class Semester(IntEnum):
    FIRST = 1
    SECOND = 2

class AssessmentTemplate(Base):
    __tablename__ = "assessment_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    
    # 1. Added the missing 'name' column so teachers can title the test
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 2. String Enum safely masked for Postgres
    type: Mapped[AssessmentType] = mapped_column(
        SQLEnum(AssessmentType, native_enum=False, length=20), 
        nullable=False, 
        default=AssessmentType.TEST
    )
    
    # 3. IntEnums safely masked as standard Integers for Postgres math
    coefficient: Mapped[Coefficient] = mapped_column(Integer, nullable=False) 
    semester: Mapped[Semester] = mapped_column(Integer, nullable=False) 

    # 4. The Handshakes (Fixed the typo here!)
    subject: Mapped["Subject"] = relationship("Subject", back_populates="templates")
    scores: Mapped[list["StudentScore"]] = relationship(
        "StudentScore", 
        back_populates="assessment_template", 
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("length(name) >= 2", name='assessment_template_name_min_length'),
    )


    # --- THE BOUNCERS (Validations) ---

    @validates('name')
    def validate_name(self, key, input_value: str):
        if not input_value or not input_value.strip():
            raise ValueError("Tên mẫu đánh giá không được để trống")
        if len(input_value.strip()) < 2:
            raise ValueError("Tên mẫu đánh giá phải có ít nhất 2 ký tự")
        return input_value.strip()

    @validates('type')
    def validate_type(self, key, input_value):
        # 1. Convert string to Enum if needed
        if isinstance(input_value, str):
            try:
                input_value = AssessmentType(input_value.lower())
            except ValueError:
                raise ValueError(f"Loại đánh giá không hợp lệ. Vui lòng chọn từ: {[e.value for e in AssessmentType]}")
        
        if not isinstance(input_value, AssessmentType):
            raise ValueError("Loại đánh giá phải là một chuỗi hoặc giá trị của AssessmentType")

        # 2. THE AUTO-FILL MAGIC: Hardwire the coefficient based on the type!
        if input_value == AssessmentType.TEST:
            self.coefficient = Coefficient.ONE
        elif input_value == AssessmentType.MIDTERM:
            self.coefficient = Coefficient.TWO
        elif input_value == AssessmentType.FINAL:
            self.coefficient = Coefficient.THREE

        return input_value

    @validates('semester')
    def validate_semester(self, key, input_value):
        if isinstance(input_value, Semester):
            return input_value
        if isinstance(input_value, int):
            try:
                return Semester(input_value)
            except ValueError:
                raise ValueError(f"Học kỳ không hợp lệ. Vui lòng chọn từ: {[e.value for e in Semester]}")
        raise ValueError("Học kỳ phải là 1 hoặc 2")
    
    @validates('subject_id')
    def validate_subject_id(self, key, input_value):
        if not input_value:
            raise ValueError("subject_id không được để trống")
        if not isinstance(input_value, int):
            raise ValueError("subject_id phải là một số nguyên hợp lệ")
        return input_value