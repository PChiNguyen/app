from uuid import uuid4
import pytest 
from sqlalchemy.orm import Session

from db.models.student import Student
from db.models.student_score import StudentScore
from db.models.assessment_template import AssessmentTemplate
from repositories.grading_repo import GradingRepository

# ==========================================
# 🏫 TESTING GRADING REPO METHODS (TEACHER'S VIEW)
# ==========================================

def test_get_classroom_all_subject_averages_by_semester(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    results: list[dict] = repo.get_classroom_all_subject_averages_by_semester(
        classroom_id=mock_student.classroom_id, 
        semester=1
    )
    result = results[0]
    assert result["student_id"] == mock_student.id
    assert result["student_name"] == mock_student.name
    assert result["sub_avg"] == mock_student_score_semester1.score

def test_get_classroom_semester_gpas(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    results: list[dict] = repo.get_classroom_semester_gpas(
        classroom_id=mock_student.classroom_id, 
        semester=1
    )
    result = results[0]
    assert result["student_id"] == mock_student.id
    assert result["student_name"] == mock_student.name
    assert result["semester_gpa"] == mock_student_score_semester1.score

def test_get_classroom_yearly_subject_averages(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student_score_semester2: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    results: list[dict] = repo.get_classroom_yearly_subject_averages(
        classroom_id=mock_student.classroom_id
    )
    if not results:
        raise AssertionError("Expected at least one result, got an empty list.")
    
    result = results[0]
    assert result["student_id"] == mock_student.id
    assert result["student_name"] == mock_student.name
    assert result["yearly_sub_avg"] == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3

def test_get_classroom_yearly_gpas(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student_score_semester2: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    results: list[dict] = repo.get_classroom_yearly_gpas(
        classroom_id=mock_student.classroom_id
    )
    if not results:
        raise AssertionError("Expected at least one result, got an empty list.")
    
    result = results[0]
    assert result["student_id"] == mock_student.id
    assert result["student_name"] == mock_student.name
    assert result["yearly_gpa"] == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3


# ==========================================
# 🎓 TESTING GRADING REPO METHODS (STUDENT'S VIEW)
# ==========================================

def test_get_student_subject_averages_by_semester(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    results: list[dict] = repo.get_student_subject_averages_by_semester(
        classroom_id=mock_student.classroom_id,
        student_id=mock_student.id, 
        semester=1
    )
    assert results[0]["student_id"] == mock_student.id
    assert results[0]["student_name"] == mock_student.name
    assert results[0]["sub_avg"] == mock_student_score_semester1.score

def test_get_student_semester_gpas(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    result: dict = repo.get_student_semester_gpa(
        classroom_id=mock_student.classroom_id,
        student_id=mock_student.id, 
        semester=1
    )
    assert result["student_id"] == mock_student.id
    assert result["student_name"] == mock_student.name
    assert result["semester_gpa"] == mock_student_score_semester1.score

def test_get_student_yearly_subject_averages(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student_score_semester2: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    results: list[dict] = repo.get_student_yearly_subject_averages(
        classroom_id=mock_student.classroom_id, 
        student_id=mock_student.id
    )
    assert results[0]["student_id"] == mock_student.id
    assert results[0]["student_name"] == mock_student.name
    assert results[0]["yearly_sub_avg"] == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3

def test_get_student_yearly_gpas(
    db_session: Session, 
    mock_student_score_semester1: StudentScore, 
    mock_student_score_semester2: StudentScore, 
    mock_student: Student
):
    repo = GradingRepository(db_session)
    result: dict = repo.get_student_yearly_gpa(
        classroom_id=mock_student.classroom_id, 
        student_id=mock_student.id
    )
    assert result["student_id"] == mock_student.id
    assert result["student_name"] == mock_student.name
    assert result["yearly_gpa"] == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3