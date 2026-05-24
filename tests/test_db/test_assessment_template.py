import sys
import os
import uuid

from db.models.student import Student

from db.models.student import Student
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.models.assessment_template import AssessmentTemplate
from db.models.subject import Subject, SubName



def test_successful_assessment_template_creation(db_session: Session):
    """Test xem có thể tạo AssessmentTemplate mới với subject_id hợp lệ không""" 
    math = Subject(name="Math")
    db_session.add(math)
    db_session.flush()  # Đảm bảo math.id đã được gán

    math_test = AssessmentTemplate(name="Math Test 1", type="Test", semester=1, subject_id=math.id)
    db_session.add(math_test)
    db_session.commit()

    # Kiểm tra xem template đã được tạo thành công chưa
    assert math_test.id is not None

import pytest
from db.models.assessment_template import AssessmentTemplate, AssessmentType, Coefficient, Semester

# ==========================================
# 1. TEST THE 'NAME' BOUNCER
# ==========================================
@pytest.mark.parametrize("invalid_name, expected_error_text", [
    ("", "không được để trống"),
    ("   ", "không được để trống"),
    (None, "không được để trống"),
    ("A", "ít nhất 2 ký tự"),
])
def test_assessment_name_invalid(invalid_name, expected_error_text):
    # 1. Create an empty template
    template = AssessmentTemplate()
    
    # 2. Assert that trying to assign the bad name raises a ValueError
    with pytest.raises(ValueError) as exc_info:
        template.name = invalid_name
        
    # 3. Double-check that the error message is exactly what we wrote
    assert expected_error_text in str(exc_info.value)

def test_assessment_name_valid_and_strips_spaces():
    template = AssessmentTemplate()
    template.name = "   Kiểm tra 15 phút   "
    
    # The bouncer should automatically clean up the extra spaces
    assert template.name == "Kiểm tra 15 phút"


# ==========================================
# 2. TEST THE 'TYPE' BOUNCER & AUTO-FILL MAGIC
# ==========================================
@pytest.mark.parametrize("invalid_type", [
    "sussy baka",       # Random string
                 # Uppercase (your validator expects lowercase 'test')
    123,                # Integer
    None,               # Null
])
def test_assessment_type_invalid(invalid_type):
    template = AssessmentTemplate()
    with pytest.raises(ValueError):
        template.type = invalid_type

@pytest.mark.parametrize("valid_type_input, expected_enum, expected_coefficient", [
    # It should accept the raw String and auto-fill the correct Coefficient IntEnum
    ("test", AssessmentType.TEST, Coefficient.ONE),
    ("midterm", AssessmentType.MIDTERM, Coefficient.TWO),
    ("final", AssessmentType.FINAL, Coefficient.THREE),
    
    # It should also accept the Enum directly
    (AssessmentType.TEST, AssessmentType.TEST, Coefficient.ONE),
])
def test_assessment_type_auto_fills_coefficient(valid_type_input, expected_enum, expected_coefficient):
    template = AssessmentTemplate()
    
    # Trigger the validator
    template.type = valid_type_input
    
    # Did it convert strings to Enums properly?
    assert template.type == expected_enum
    
    # THE BIG REVEAL: Did the auto-fill magic work?
    assert template.coefficient == expected_coefficient


# ==========================================
# 3. TEST THE 'SEMESTER' BOUNCER
# ==========================================
@pytest.mark.parametrize("invalid_semester", [
    3,      # Semester 3 doesn't exist
    0,      # Semester 0 doesn't exist
    "one",  # Text
    None,   # Null
])
def test_semester_invalid(invalid_semester):
    template = AssessmentTemplate()
    with pytest.raises(ValueError):
        template.semester = invalid_semester


def test_hacker_insert_invalid_assessment_template(db_session: Session):
    """Test xem có thể chèn thẳng dữ liệu không hợp lệ vào DB được không""" 
    sql= text("""INSERT INTO assessment_templates(id,subject_id,name,type,coefficient,semester)
              VALUES(:id,:subject_id,:name,:type,:coefficient,:semester)""")
    data= {
        'id': 1,
        'subject_id': 999, # subject_id không tồn tại nhưng sẽ được chèn thẳng vào DB
        'name': 'Hacker Test',
        'type': 'invalid_type', # type không hợp lệ nhưng sẽ được chèn thẳng vào DB
        'coefficient': 999, # coefficient không hợp lệ nhưng sẽ được chèn thẳng vào DB
        'semester': 999, # semester không hợp lệ nhưng sẽ được chèn thẳng vào DB
    }
    with pytest.raises(IntegrityError) as e:
        db_session.execute(sql,data)
        db_session.commit()
    print(f'{e}')

    db_session.rollback()

def test_assessment_template_subject_relationship(db_session: Session):
    """Test xem quan hệ giữa AssessmentTemplate và Subject có hoạt động không""" 

    math = Subject(name="Math")
    db_session.add(math)
    db_session.flush()  # Đảm bảo math.id đã được gán

    math_test = AssessmentTemplate(name="Math Test 1", type="Test", semester=1, subject_id=math.id)
    db_session.add(math_test)
    db_session.commit()

    # Kiểm tra quan hệ ngược lại từ AssessmentTemplate
    assert math_test.subject.name == SubName.MATH

def test_assessment_template_student_scores_relationship(db_session: Session, mock_student: Student):
    """Test xem quan hệ giữa AssessmentTemplate và StudentScore có hoạt động không""" 
    # 1. Tạo Subject
    math = Subject(name="Math")
    db_session.add(math)
    db_session.flush()  # Đảm bảo math.id đã được gán

    # 2. Tạo AssessmentTemplate
    math_test = AssessmentTemplate(name="Math Test 1", type="Test", semester=1, subject_id=math.id)
    db_session.add(math_test)
    db_session.flush()  # Đảm bảo math_test.id đã được gán

    # 3. Tạo StudentScore liên kết với AssessmentTemplate
    from db.models.student_score import StudentScore
    score = StudentScore(student_id=mock_student.id, assessment_template_id=math_test.id, score=9.5)
    db_session.add(score)
    db_session.commit()

    # Kiểm tra quan hệ ngược lại từ AssessmentTemplate
    assert len(math_test.scores) == 1
    assert math_test.scores[0].score == 9.5




