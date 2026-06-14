from services.student_score_service import StudentScoreService
from db.models.student_score import StudentScore
from db.models.assessment_template import AssessmentTemplate
from db.models.subject import Subject
from db.models.student import Student
import pytest
from fastapi import HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session


def student_score_service(db_session: Session):
    return StudentScoreService(db_session) 


    

## test create student score
def test_bulk_create_student_scores_invalid_student(db_session: Session):
    list_of_students_ids = [uuid4(), uuid4()]
    service = student_score_service(db_session) 
    with pytest.raises(HTTPException) as exc_info:
        service.bulk_create_empty_slots(4, list_of_students_ids)
    assert exc_info.value.status_code == 404

## test update student score
def test_update_student_score_not_found(db_session):
    service = student_score_service(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.update_score(uuid4(), 85)
    assert exc_info.value.status_code == 404

## test get student score by student id 
def test_get_student_score_by_student_id_not_found(db_session):
    service = student_score_service(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_scores_by_student_id(uuid4())
    assert exc_info.value.status_code == 404 

def test_get_scores_by_template_id_not_found(db_session):
    service = student_score_service(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_scores_by_template_id(uuid4())
    assert exc_info.value.status_code == 404

def test_get_scores_by_student_id_and_subject_id_not_found(db_session):
    service = student_score_service(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_scores_by_student_id_and_subject_id(uuid4(), 1)
    assert exc_info.value.status_code == 404 




def test_bulk_create_empty_slots_success(db_session, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
    service = student_score_service(db_session)
    # Simulating a teacher distributing blank tests to the classroom
    slots = service.bulk_create_empty_slots(
        template_id=mock_assessment_template_semester1.id, 
        student_ids=[mock_student.id]
    )
    assert isinstance(slots, list)
    assert len(slots) == 1
    assert slots[0].score is None  # Defaults to None!

def test_update_score_success(db_session, mock_student_score_semester1):
    service = student_score_service(db_session)
    # Teacher grades the paper and updates it to a 10
    updated_score = service.update_score(mock_student_score_semester1.id, new_score=10.0)
    assert updated_score.score == 10.0

def test_get_scores_by_student_id_success(db_session, mock_student: Student, mock_student_score_semester1):
    service = student_score_service(db_session)
    scores = service.get_scores_by_student_id(mock_student.id)
    assert isinstance(scores, list)
    assert len(scores) >= 1

def test_get_scores_by_template_id_success(db_session, mock_assessment_template_semester1: AssessmentTemplate, mock_student_score_semester1):
    service = student_score_service(db_session)
    scores = service.get_scores_by_template_id(mock_assessment_template_semester1.id)
    assert isinstance(scores, list)
    assert len(scores) >= 1

def test_get_scores_by_student_id_and_subject_id_success(db_session, mock_student: Student, mock_subject: Subject, mock_student_score_semester1):
    service = student_score_service(db_session)
    scores = service.get_scores_by_student_id_and_subject_id(mock_student.id, mock_subject.id)
    assert isinstance(scores, list)
    assert len(scores) >= 1






