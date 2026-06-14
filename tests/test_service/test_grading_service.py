from services.grading_service import GradingService
from fastapi import HTTPException
from sqlalchemy.orm import Session 
import pytest 
from db.models.classroom import Classroom 
from db.models.student import Student 


def test_get_classroom_all_subject_averages_by_semester(db_session: Session, mock_classroom: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_classroom_all_subject_averages_by_semester(mock_classroom.id, 1)
    assert exc_info.value.status_code == 404 

def test_get_classroom_semester_gpas(db_session: Session, mock_classroom: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_classroom_semester_gpas(mock_classroom.id, 1)
    assert exc_info.value.status_code == 404

def test_get_classroom_yearly_gpas(db_session: Session, mock_classroom: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_classroom_yearly_gpas(mock_classroom.id)
    assert exc_info.value.status_code == 404 

def test_get_classroom_yearly_subject_averages(db_session: Session, mock_classroom: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_classroom_yearly_subject_averages(mock_classroom.id)
    assert exc_info.value.status_code == 404


## testing student get functions 

def test_get_student_subject_averages_by_semester(db_session: Session, mock_classroom: Classroom, mock_student: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_student_subject_averages_by_semester(mock_classroom.id, mock_student.id, 1)
    assert exc_info.value.status_code == 404

def test_get_student_semester_gpa(db_session: Session, mock_classroom: Classroom, mock_student: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_student_semester_gpa(mock_classroom.id, mock_student.id, 1)
    assert exc_info.value.status_code == 404

def test_get_student_yearly_subject_averages(db_session: Session, mock_classroom: Classroom, mock_student: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_student_yearly_subject_averages(mock_classroom.id, mock_student.id)
    assert exc_info.value.status_code == 404

def test_get_student_yearly_gpa(db_session: Session, mock_classroom: Classroom, mock_student: Classroom):
    grading_service = GradingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        grading_service.get_student_yearly_gpa(mock_classroom.id, mock_student.id)
    assert exc_info.value.status_code == 404




# --- CLASSROOM VIEWS ---
def test_get_classroom_all_subject_averages_by_semester_success(db_session, mock_classroom: Classroom, mock_student_score_semester1):
    service = GradingService(db_session)
    averages = service.get_classroom_all_subject_averages_by_semester(mock_classroom.id, 1)
    assert isinstance(averages, list)
    assert len(averages) >= 1

def test_get_classroom_semester_gpas_success(db_session, mock_classroom: Classroom, mock_student_score_semester1):
    service = GradingService(db_session)
    gpas = service.get_classroom_semester_gpas(mock_classroom.id, 1)
    assert isinstance(gpas, list)
    assert len(gpas) >= 1

def test_get_classroom_yearly_subject_averages_success(db_session, mock_classroom: Classroom, mock_student_score_semester1, mock_student_score_semester2):
    service = GradingService(db_session)
    averages = service.get_classroom_yearly_subject_averages(mock_classroom.id)
    assert isinstance(averages, list)

def test_get_classroom_yearly_gpas_success(db_session, mock_classroom: Classroom, mock_student_score_semester1, mock_student_score_semester2):
    service = GradingService(db_session)
    gpas = service.get_classroom_yearly_gpas(mock_classroom.id)
    assert isinstance(gpas, list)

# --- STUDENT VIEWS ---
def test_get_student_subject_averages_by_semester_success(db_session, mock_classroom: Classroom, mock_student: Student, mock_student_score_semester1):
    service = GradingService(db_session)
    averages = service.get_student_subject_averages_by_semester(mock_classroom.id, mock_student.id, 1)
    assert averages is not None

def test_get_student_semester_gpa_success(db_session, mock_classroom: Classroom, mock_student: Student, mock_student_score_semester1):
    service = GradingService(db_session)
    gpa = service.get_student_semester_gpa(mock_classroom.id, mock_student.id, 1)
    assert gpa is not None

def test_get_student_yearly_subject_averages_success(db_session, mock_classroom: Classroom, mock_student: Student, mock_student_score_semester1, mock_student_score_semester2):
    service = GradingService(db_session)
    averages = service.get_student_yearly_subject_averages(mock_classroom.id, mock_student.id)
    assert averages is not None

def test_get_student_yearly_gpa_success(db_session, mock_classroom: Classroom, mock_student: Student, mock_student_score_semester1, mock_student_score_semester2):
    service = GradingService(db_session)
    gpa = service.get_student_yearly_gpa(mock_classroom.id, mock_student.id)
    assert gpa is not None