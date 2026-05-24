import sys
import os
import uuid

from db.models.assessment_template import AssessmentTemplate
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
import pytest 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from db.models.subject import Subject, SubName

def test_validate_name_enum():
    """Test xem có ép kiểu string sang Enum tự động được không""" 
    s = Subject(name="Math")
    assert s.name == SubName.MATH

    s2 = Subject(name=SubName.PHYSICS)
    assert s2.name == SubName.PHYSICS
@pytest.mark.parametrize("invalid_name", [
    "   ",  # Empty string with spaces
    "",     # Truly empty string
    123,    # Not a string at all
    "A",    # Too short if we had a length check
])
def test_subject_validators_all_cases(db_session: Session, invalid_name):
    """Test tất cả các trường hợp lỗi có thể xảy ra với tên môn học""" 
    with pytest.raises(ValueError) as exinfo:
        subject = Subject(name=invalid_name)
        db_session.add(subject)
        db_session.commit()
    print(f"Đã bắt được lỗi như mong đợi: {exinfo.value}")

def test_hacker_insert_invalid_subject_name(db_session: Session):
    """Test xem có thể chèn thẳng tên môn học không hợp lệ vào DB được không""" 
    sql= text("""INSERT INTO subjects(id,name)
              VALUES(:id,:name)""")
    data= {
        'id': 1,
        'name': 'N', # tên không hợp lệ nhưng sẽ được chèn thẳng vào DB
    }
    with pytest.raises(IntegrityError) as e:
        db_session.execute(sql,data)
        db_session.commit()
    print(f'{e}')

    db_session.rollback()


def test_subject_assessment_template_relationship(db_session: Session):
    """Test xem quan hệ giữa Subject và AssessmentTemplate có hoạt động không""" 
    math = Subject(name="Math")
    physics = Subject(name="Physics")
    db_session.add_all([math, physics])
    db_session.flush()  # Đảm bảo math.id và physics.id đã được gán

    math_test = AssessmentTemplate(name="Math Test 1", type="Test", semester=1, subject_id=math.id)
    physics_midterm = AssessmentTemplate(name="Physics Midterm", type="Midterm", semester=2, subject_id=physics.id)
    db_session.add_all([math_test, physics_midterm])
    db_session.commit()

    # Kiểm tra quan hệ ngược lại từ AssessmentTemplate
    assert math_test.subject.name == SubName.MATH
    assert physics_midterm.subject.name == SubName.PHYSICS

    


