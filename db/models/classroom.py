import uuid 
import re 
from sqlalchemy import String, ForeignKey, CheckConstraint,UUID  

from sqlalchemy.orm import Mapped, mapped_column , relationship, validates 

from db.base import Base 
class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid= True),
                                         primary_key= True,
                                         default= uuid.uuid4)
    
    name: Mapped[str]= mapped_column(String,
                                     nullable= False
                            )
    teacher_id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid= True),
                                                 ForeignKey('users.id', ondelete= "RESTRICT"),
                                                 nullable= True,
                                                 index= True)
    teacher= relationship('User', back_populates='classrooms')

    students= relationship('Student',back_populates='classroom', cascade= "save-update, merge")



    __table_args__= (
        CheckConstraint("length(name) >= 2", name='classroom_name_min_length'),)
    
    @validates('name')
    def validate_name(self, key, input_value: str):
        if not input_value.strip():
            raise ValueError("Tên lớp học không được để trống hoặc chỉ có khoảng trắng")
        if not isinstance(input_value, str):
            raise ValueError("Tên lớp học phải là một chuỗi")
        if not re.match(r'^[a-zA-Z\s]+$', input_value):
            raise ValueError("Tên lớp học chỉ được chứa chữ cái và khoảng trắng")
        if len(input_value.strip()) < 2:
            raise ValueError("Tên lớp học phải có ít nhất 2 ký tự")
        
        return input_value.strip()
    @validates('teacher_id')
    def validate_teacher_id(self, key, input_value):
        if not input_value:
            raise ValueError("teacher_id không được để trống")
        if not isinstance(input_value, uuid.UUID):
            raise ValueError("teacher_id phải là một UUID hợp lệ")
        return input_value
    