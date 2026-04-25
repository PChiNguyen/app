import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

import pytest 
from db.models.classroom import Classroom  
from db.models.user import User    
from db.models.student import Student   
from sqlalchemy import text 

from sqlalchemy.exc import IntegrityError



def test_validate_classroom_name_too_short():
    with pytest.raises(ValueError) as exinfo:
        Classroom(name="A", teacher_id= uuid.uuid4())
def test_validate_classroom_name_invalid_characters():
    with pytest.raises(ValueError) as exinfo:
        Classroom(name="Math101!", teacher_id= uuid.uuid4())
def test_validate_teacher_id_invalid():
    with pytest.raises((ValueError,IntegrityError)) as exinfo:
        Classroom(name="Math", teacher_id= "not-a-uuid") 
def test_classroom_with_nonexistent_teacher(db_session):
    with pytest.raises(IntegrityError) as exinfo:
        db_session.add(Classroom(name="Math", teacher_id= uuid.uuid4()))
        db_session.commit()
    

### Test ở db 

def test_hacker_insert_invalid_classroom_name(db_session):
    teacher= User(username="teacher1",
                    email="teacher1@abc.com",
                        password_hash="abc",
                        role="teacher")
    db_session.add(teacher)
    db_session.flush()
    db_session.refresh(teacher)


    classroom= Classroom(name="Math", teacher_id= teacher.id)
    db_session.add(classroom)
    db_session.commit()
    """Test dùng SQL thuần (Bind Parameters) để giả lập lách luật""" 
    sql=text("""
        INSERT INTO classrooms (id, name, teacher_id)
        VALUES (:id, :name, :teacher_id)
    """)
    params = {
        'id': str(uuid.uuid4()),
        'name': 'Igle',  # Tên không hợp lệ nhưng sẽ được chèn thẳng vào DB
        'teacher_id': str(uuid.uuid4())
    }
    with pytest.raises(IntegrityError) as e:
        db_session.execute(sql, params)
        db_session.commit()
    print(f'{e}')
    db_session.rollback()

    db_session.rollback() 


def test_relationship(db_session):
    """Test xem quan hệ giữa Classroom và User có hoạt động không""" 

    teacher= User(username="teacher1",
                    email="teacher1@abc.com",
                        password_hash="abc",
                        role="teacher")
    
    db_session.add(teacher)
    db_session.flush()

    eng_class= Classroom(name="English", teacher_id=teacher.id)
    db_session.add(eng_class)
    db_session.flush()

    student1= Student(name="Student One", classroom_id=eng_class.id)
    student2= Student(name="Student Two", classroom_id=eng_class.id)
    db_session.add_all([student1, student2])
    db_session.commit() 

    db_session.refresh(eng_class)


    assert eng_class.teacher.username == "teacher1"
    assert len(eng_class.students) == 2 
    assert eng_class.students[0].name == "Student One"
    assert eng_class.students[1].name == "Student Two"

    assert student1.classroom.name == "English"
    assert student2.classroom.name == "English"    






    


    



    

      



