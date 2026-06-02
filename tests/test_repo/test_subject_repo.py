import pytest 
from db.models.subject import Subject
from repositories.subject_repo import SubjectRepository



def test_get_all(db_session):
    subject_repo = SubjectRepository(db_session)
    subjects = subject_repo.get_all()
    assert len(subjects) == 0

def test_get_by_id(db_session, mock_subject: Subject):
    subject_repo = SubjectRepository(db_session)
    subject = subject_repo.get_by_id(mock_subject.id)
    assert subject is not None
    assert subject.id == mock_subject.id
    assert subject.name == mock_subject.name

def test_get_by_name(db_session, mock_subject: Subject):
    subject_repo = SubjectRepository(db_session)
    subject = subject_repo.get_by_name(mock_subject.name)
    assert subject is not None
    assert subject.id == mock_subject.id
    assert subject.name == mock_subject.name






    