from services.subject_service import SubjectService
from db.models.subject import Subject, SubName
import pytest
from fastapi import HTTPException

## test create subject
def test_create_subject_duplicate_name(db_session, mock_subject: Subject):
    service = SubjectService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.create_subject(mock_subject.name)
    assert exc_info.value.status_code == 400 
## test get all subjects
def test_get_all_subjects_not_found(db_session):
    service = SubjectService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_all_subjects()
    assert exc_info.value.status_code == 404

## test get subject by id
def test_get_subject_by_id_not_found(db_session):
    service = SubjectService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_subject_by_id(9999)
    assert exc_info.value.status_code == 404

## test get subject by name
def test_get_subject_by_name_not_found(db_session):
    service = SubjectService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_subject_by_name("Nonexistent Subject")
    assert exc_info.value.status_code == 404 


def test_create_subject_success(db_session):
    service = SubjectService(db_session)
    new_subject = service.create_subject("Computer Science")
    assert new_subject is not None
    assert new_subject.id is not None
    assert new_subject.name == SubName.COMPUTER_SCIENCE 

def test_get_all_subjects_success(db_session, mock_subject: Subject):
    service = SubjectService(db_session)
    subjects = service.get_all_subjects()
    # Ensure it returns a list and contains our mock subject
    assert isinstance(subjects, list)
    assert len(subjects) >= 1
    assert any(sub.name == SubName.MATH for sub in subjects)

def test_get_subject_by_id_success(db_session, mock_subject: Subject):
    service = SubjectService(db_session)
    subject = service.get_subject_by_id(mock_subject.id)
    assert subject.name == SubName.MATH

def test_get_subject_by_name_success(db_session, mock_subject: Subject):
    service = SubjectService(db_session)
    # Testing the alternative lookup method
    subject = service.get_subject_by_name('Math')
    assert subject.id == mock_subject.id