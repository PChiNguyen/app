# db/models/subject.py
import enum

from sqlalchemy import String, Integer, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from db.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from db.models.assessment_template import AssessmentTemplate
    from db.models.user import User
import enum
class SubName(enum.Enum):
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    LITERATURE = "literature"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    BIOLOGY = "biology"
    COMPUTER_SCIENCE = "computer science"
    ENGLISH = "english"
    OTHER = "other"

class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[SubName] = mapped_column(SQLEnum(SubName, native_enum=False, length=100), unique=True, index=True, nullable=False)

    # THE MAGIC: A subject has many templates. 
    # 'back_populates' tells SQLAlchemy to look for a variable named 'subject' in the other file.
    templates: Mapped[list["AssessmentTemplate"]] = relationship(
        "AssessmentTemplate", 
        back_populates="subject",
        cascade="all, delete-orphan" # If you delete Math, it deletes all Math tests automatically!
    )
    # We name it 'teachers' because our CheckConstraint guarantees 
    # that only users with the role of 'teacher' will ever be linked here!
    teachers: Mapped[list["User"]] = relationship('User', back_populates='subject')

    __table_args__= (
        CheckConstraint("length(name) >= 2", name='subject_name_min_length'),) 

    @validates('name')
    def validate_name(self, key, input_value: SubName):
        if isinstance(input_value,SubName):
            return input_value
        if isinstance(input_value,str):
            try:
                return SubName(input_value.lower())
            except ValueError:
                raise ValueError(f"'{input_value}' không phải là môn học hợp lệ. Vui lòng chọn từ: {[e.value for e in SubName]}")
        raise ValueError("Tên môn học phải là một chuỗi hoặc một giá trị của Enum SubName")

        
    

