import sys
import os
import uuid
import pytest
from sqlalchemy.exc import IntegrityError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from repositories.user_repo import UserRepository
from repositories.classroom_repo import ClassroomRepository
from repositories.student_repo import StudentRepository
from repositories.grade_repo import GradeRepository
from db.models.grade import SubjectCoefficient

# ==========================================
# FIXTURES (The Dependency Chain)
# ==========================================

@pytest.fixture
def teacher(db_session):
    return UserRepository(db_session).create(
        username=f"teacher_{uuid.uuid4().hex[:6]}", 
        email=f"teacher_{uuid.uuid4().hex[:6]}@school.com",
        password="secure_hash",
        role="teacher"
    )

@pytest.fixture
def classroom(db_session, teacher):
    return ClassroomRepository(db_session).create(
        name="Mathematics", 
        teacher_id=teacher.id
    )

@pytest.fixture
def student(db_session, classroom):
    # Notice we return the actual Student object, not just the ID
    return StudentRepository(db_session).create(
        name="Thảo Nguyên", 
        classroom_id=classroom.id
    )

@pytest.fixture
def grade_repo(db_session):
    return GradeRepository(db_session)

# ==========================================
# TESTS
# ==========================================

def test_create_grade(grade_repo, student):
    grade = grade_repo.create(
        subject="Toán Học", 
        score=9.5, 
        student_id=student.id, 
        coefficient=SubjectCoefficient.FINAL
    )
    assert grade.id is not None
    assert grade.score == 9.5
    assert grade.subject == "Toán Học"

def test_create_grade_invalid_student(grade_repo):
    with pytest.raises(IntegrityError):
        grade_repo.create(
            subject="Vật Lý", 
            score=8.0, 
            student_id=uuid.uuid4() # Fake UUID
        )

def test_get_grade_by_id(grade_repo, student):
    created_grade = grade_repo.create(
        subject="Hóa Học", score=8.5, student_id=student.id
    )
    fetched_grade = grade_repo.get_by_id(created_grade.id)
    
    assert fetched_grade is not None
    assert fetched_grade.subject == "Hóa Học"

def test_get_by_student_id(grade_repo, student):
    grade_repo.create(subject="Toán Học", score=9.0, student_id=student.id)
    grade_repo.create(subject="Ngữ Văn", score=8.0, student_id=student.id)
    
    grades = grade_repo.get_by_student_id(student.id)
    
    assert len(grades) == 2
    # Convert list of objects to list of strings for easy assertion
    subjects = [g.subject for g in grades]
    assert "Toán Học" in subjects
    assert "Ngữ Văn" in subjects

def test_update_grade(grade_repo, student):
    grade = grade_repo.create(subject="Sinh Học", score=5.0, student_id=student.id)
    
    # Teacher realizes they made a mistake and bumps the score
    updated_grade = grade_repo.update(grade.id, score=9.5, coefficient=SubjectCoefficient.MIDTERM)
    
    assert updated_grade is not None
    assert updated_grade.score == 9.5
    assert updated_grade.coefficient == SubjectCoefficient.MIDTERM

def test_delete_grade(grade_repo, student):
    grade = grade_repo.create(subject="Lịch Sử", score=10.0, student_id=student.id)
    
    result = grade_repo.delete(grade.id)
    assert result is True
    
    # Verify it's actually gone
    deleted_grade = grade_repo.get_by_id(grade.id)
    assert deleted_grade is None

def test_get_multi_by_subject(grade_repo, student, db_session):
    # Need a second student to prove it filters across students
    student2 = StudentRepository(db_session).create(name="Học Sinh Hai", classroom_id=student.classroom_id)
    
    grade_repo.create(subject="Tiếng Anh", score=9.0, student_id=student.id)
    grade_repo.create(subject="Tiếng Anh", score=8.5, student_id=student2.id)
    grade_repo.create(subject="Toán Học", score=10.0, student_id=student.id) # Should not be fetched
    
    english_grades = grade_repo.get_multi_by_subject("Tiếng Anh")
    
    assert len(english_grades) == 2
    for g in english_grades:
        assert g.subject == "Tiếng Anh"