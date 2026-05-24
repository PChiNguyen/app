
import sys
import os
import uuid

from db.session import Sessionlocal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.models.student import Student
from db.models.classroom import Classroom
from db.models.user import User


def test_student_validation_all_cases():
    # Test tên trống
    with pytest.raises(ValueError, match="không được để trống"):
        Student(name="   ", classroom_id=uuid.uuid4())
    
    # Test tên quá ngắn
    with pytest.raises(ValueError, match="ít nhất"): # Giả sử ông có check độ dài
        Student(name="A", classroom_id=uuid.uuid4())
        
    # Test tên chứa ký tự đặc biệt
    with pytest.raises(ValueError, match="chỉ được chứa chữ cái"):
        Student(name="Hacker123", classroom_id=uuid.uuid4())

    # Test classroom_id sai định dạng
    with pytest.raises(ValueError, match="phải là một UUID"):
        Student(name="Nguyen Van A", classroom_id="not-a-uuid") 


### test ở db 

def test_hacker_insert_invalid_student_name(db_session: Session):
    sql= text("""INSERT INTO students(id,name,classroom_id)
              VALUES(:id,:name,:class_id)""")
    data= {
        'id': str(uuid.uuid4()),
        'name': 'N', # tên không hợp lệ nhưng sẽ được chèn thẳng vào DB
        'class_id': str(uuid.uuid4())
    }
    with pytest.raises(IntegrityError) as e:
        db_session.execute(sql,data)
        db_session.commit()
    print(f'{e}')

    db_session.rollback()  

    


def test_student_classroom_relationship(db_session: Session):
    """Test xem quan hệ giữa Student và Classroom có hoạt động không""" 
    teacher= User(username="teacher1",
                    email="teacher1@abc.com",
                     password_hash="password123")
    db_session.add(teacher)
    db_session.flush()
    math_class= Classroom(name="Math", teacher_id=teacher.id)
    db_session.add(math_class)
    db_session.flush()
    student1= Student(name="Thảo Nguyên", classroom_id=math_class.id)
    student2= Student(name="Student Two", classroom_id=math_class.id)
    db_session.add_all([student1, student2])
    db_session.commit()
    db_session.refresh(math_class)
    assert math_class.teacher.username == "teacher1"
    assert len(math_class.students) == 2 
    assert math_class.students[0].name == "Thảo Nguyên"
    assert math_class.students[1].name == "Student Two"
    assert student1.classroom.name == "Math"
    assert student2.classroom.name == "Math"
def test_student_with_nonexistent_classroom(db_session: Session):
    with pytest.raises(IntegrityError) as exinfo:
        db_session.add(Student(name="Student Three", classroom_id= uuid.uuid4()))
        db_session.commit() 







 