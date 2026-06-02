import pytest 
from uuid import uuid4
from db.models.assessment_template import AssessmentTemplate
from schemas.student_score_schemas import StudentScoreCreate, StudentScoreResponse, StudentScoreUpdate
from pydantic import ValidationError
from db.models.student_score import Status
from db.models.student import Student
from db.models.assessment_template import AssessmentTemplate

def test_create_student_score_success(mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
    """Tests that valid data creates a student score successfully"""
    data = {
        "student_id": mock_student.id,
        "assessment_template_id": mock_assessment_template_semester1.id,
        "score": 8.5
    }
    score = StudentScoreCreate(**data)
    assert score.student_id == data["student_id"]
    assert score.assessment_template_id == data["assessment_template_id"]
    assert score.score == data["score"]
@pytest.mark.parametrize("invalid_score", [-1, 11]) # Testing scores outside the valid range
def test_create_student_score_score_constraints(invalid_score, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
    """Tests various invalid score values in one go"""
    data = {
        "student_id": mock_student.id,
        "assessment_template_id": mock_assessment_template_semester1.id,
        "score": invalid_score
    }
    with pytest.raises(ValidationError):
        StudentScoreCreate(**data)