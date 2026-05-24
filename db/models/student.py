import uuid
import re 
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, CheckConstraint,UUID as SQLUUID  
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates 
from db.base import Base
if TYPE_CHECKING:
    from db.models.classroom import Classroom
    from db.models.student_score import StudentScore
class Student(Base):
    __tablename__= 'students'

    id: Mapped[uuid.UUID]= mapped_column(SQLUUID(as_uuid= True),
                                         primary_key= True,
                                         default= uuid.uuid4)
    
    name: Mapped[str]= mapped_column(String,nullable=False,index= True)
    # name ít nên không cần đánh index 

    

    classroom_id: Mapped[uuid.UUID]= mapped_column(SQLUUID(as_uuid= True),
                                                   ForeignKey('classrooms.id',ondelete= 'SET NULL'),
                                                   nullable= True
                                                
                                                   )
    classroom: Mapped["Classroom"]= relationship('Classroom', back_populates='students')
    # Use Mapped[list["StudentScore"]]!
    student_scores: Mapped[list["StudentScore"]]= relationship('StudentScore', back_populates='student', cascade="all, delete-orphan")


    __table_args__= (
        CheckConstraint("length(name) >= 2", name='student_name_min_length'),) 
    
    @validates('name')
    def validate_name(self, key, input_value: str):
        if not input_value or not input_value.strip():
            raise ValueError("Tên không được để trống")
        
        # Remove spaces temporarily just to check the letters
        name_no_spaces = input_value.replace(" ", "")
        
        # .isalpha() automatically allows 'Thảo Nguyên' but blocks 'Nguyên 123' or 'Nguyên!'
        if not name_no_spaces.isalpha():
            raise ValueError("Tên học sinh chỉ được chứa chữ cái và khoảng trắng")
        if len(input_value.strip()) < 2:
            raise ValueError("Tên học sinh phải có ít nhất 2 ký tự")
            
        return input_value.strip()
    @validates('classroom_id')
    def validate_classroom_id(self, key, input_value):
        if not input_value:
            raise ValueError("classroom_id không được để trống")
        if not isinstance(input_value, uuid.UUID):
            raise ValueError("classroom_id phải là một UUID hợp lệ")
        return input_value 
    
    
    
    
    
        
        

        
        






    