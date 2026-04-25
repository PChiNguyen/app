import sys
import os
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Ensure imports work regardless of where pytest is run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from db.models.student import Student
from db.models.grade import Grade, SubjectCoefficient

# ==========================================
# 1. PYTHON-LEVEL VALIDATION TESTS (@validates)
# ==========================================

def test_grade_subject_validation():
    student_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="không được để trống"):
        Grade(subject="   ", score=8.5, student_id=student_id)
        
    with pytest.raises(ValueError, match="chỉ được chứa chữ cái, số"):
        Grade(subject="Toán Học @#$", score=8.5, student_id=student_id)

def test_grade_score_validation():
    student_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="không được để trống"):
        Grade(subject="Toán", score=None, student_id=student_id)
        
    with pytest.raises(ValueError, match="số thực"):
        Grade(subject="Toán", score="Chín phẩy năm", student_id=student_id)
        
    with pytest.raises(ValueError, match="từ 0 đến 10"):
        Grade(subject="Toán", score=10.5, student_id=student_id)
        
    with pytest.raises(ValueError, match="từ 0 đến 10"):
        Grade(subject="Toán", score=-1.0, student_id=student_id)

def test_grade_coefficient_validation():
    student_id = uuid.uuid4()
    
    with pytest.raises(ValueError, match="không hợp lệ"):
        # 4 is not in our Enum (1, 2, 3)
        Grade(subject="Toán", score=8.0, coefficient=4, student_id=student_id)

def test_grade_student_id_validation():
    with pytest.raises(ValueError, match="UUID hợp lệ"):
        Grade(subject="Toán", score=8.0, student_id="not-a-real-uuid")


# ==========================================
# 2. DATABASE-LEVEL TESTS (Integrity & Cascade)
# ==========================================

def test_hacker_bypass_python_score_check(db_session):
    """
    Bypass Python's @validates by injecting raw SQL.
    This proves our DB-level CheckConstraint('score >= 0 AND score <= 10') actually works.
    """
    # Create a dummy student first to satisfy the Foreign Key
    student = Student(name="Dummy Student")
    db_session.add(student)
    db_session.flush()

    sql = text("""
        INSERT INTO grades (id, student_id, subject, score, coefficient) 
        VALUES (:id, :student_id, :subject, :score, :coeff)
    """)
    data = {
        'id': str(uuid.uuid4()),
        'student_id': str(student.id),
        'subject': 'Hacker Math',
        'score': 99.9, # DB should reject this!
        'coeff': 1
    }
    
    with pytest.raises(IntegrityError):
        db_session.execute(sql, data)
        db_session.commit()
        
    db_session.rollback()

def test_grade_student_relationship_and_cascade(db_session):
    """
    Test that a Student can have multiple grades, 
    and deleting the Student wipes the grades from the DB (CASCADE).
    """
    # 1. Setup Student and Grades
    student = Student(name="Thảo Nguyên")
    db_session.add(student)
    db_session.flush()

    grade1 = Grade(
        subject="Toán", 
        score=9.5, 
        student_id=student.id, 
        coefficient=SubjectCoefficient.FINAL
    )
    grade2 = Grade(
        subject="Vật Lý", 
        score=8.0, 
        student_id=student.id, 
        coefficient=SubjectCoefficient.MIDTERM
    )
    
    db_session.add_all([grade1, grade2])
    db_session.commit()

    # 2. Verify Relationship mapping
    assert len(student.grades) == 2
    assert grade1.student.name == "Thảo Nguyên"

    # 3. Test The CASCADE Delete
    db_session.delete(student)
    db_session.commit()

    # 4. Verify Ghost Grades are gone
    remaining_grades = db_session.query(Grade).filter_by(student_id=student.id).all()
    assert len(remaining_grades) == 0