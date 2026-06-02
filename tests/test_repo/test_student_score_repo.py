import pytest
from db.models.student import Student
from db.models.student_score import StudentScore
from repositories.student_score_repo import StudentScoreRepository  
from db.models.assessment_template import AssessmentTemplate
from sqlalchemy.orm import Session  

@pytest.fixture
def mock_students(db_session: Session) -> list[Student]:
    from db.models.student import Student
    students = []
    for i in range(5):
        student = Student(name=f"Student")
        db_session.add(student)
        students.append(student)
    db_session.commit()
    for student in students:
        db_session.refresh(student)
    return students

def test_bulk_create_empty_slots(db_session, mock_assessment_template_semester1: AssessmentTemplate, mock_students):
    repo = StudentScoreRepository(db_session)
    student_ids = [student.id for student in mock_students]
    scores = repo.bulk_create_empty_slots(mock_assessment_template_semester1.id, student_ids)
    
    assert len(scores) == len(student_ids)
    for score in scores:
        assert score.assessment_template_id == mock_assessment_template_semester1.id
        assert score.score is None

def test_update_score(db_session, mock_student_score_semester1: StudentScore):
    repo = StudentScoreRepository(db_session)
    new_score = 9.0
    updated_score = repo.update_score(mock_student_score_semester1.id, new_score)
    
    assert updated_score is not None
    assert updated_score.id == mock_student_score_semester1.id
    assert updated_score.score == new_score

def test_get_by_id(db_session, mock_student_score_semester1: StudentScore):
    repo = StudentScoreRepository(db_session)
    score = repo.get_by_id(mock_student_score_semester1.id)
    
    assert score is not None
    assert score.id == mock_student_score_semester1.id
    assert score.student_id == mock_student_score_semester1.student_id
    assert score.assessment_template_id == mock_student_score_semester1.assessment_template_id
    assert score.score == mock_student_score_semester1.score

def test_get_by_student_id(db_session, mock_student_score_semester1: StudentScore):
    repo = StudentScoreRepository(db_session)
    scores = repo.get_by_student_id(mock_student_score_semester1.student_id)
    
    assert len(scores) > 0
    for score in scores:
        assert score.student_id == mock_student_score_semester1.student_id

def test_get_by_template_id(db_session, mock_student_score_semester1: StudentScore):
    repo = StudentScoreRepository(db_session)
    scores = repo.get_by_template_id(mock_student_score_semester1.assessment_template_id)
    
    assert len(scores) > 0
    for score in scores:
        assert score.assessment_template_id == mock_student_score_semester1.assessment_template_id