import pytest 
from uuid import uuid4
from schemas.assessment_template_schemas import AssessmentTemplateCreate, AssessmentTemplateResponse
from pydantic import ValidationError  

def test_create_assessment_template_success(mock_subject):
    """Tests that valid data creates an assessment template successfully"""
    data = {
        "name": "15 phút lần 1",
        "type": "test",
        "semester": 1,
        "subject_id": mock_subject.id
    }
    template = AssessmentTemplateCreate(**data)
    assert template.name == data["name"]
    assert template.type == data["type"]
    assert template.semester == data["semester"]
    assert template.subject_id == data["subject_id"]

@pytest.mark.parametrize("invalid_type", ["", "invalid_type", "TEST"]) # Testing empty and invalid types
def test_create_assessment_template_type_constraints(invalid_type, mock_subject):    
    """Tests various invalid assessment types in one go"""
    data = {
        "name": "15 phút lần 1",
        "type": invalid_type,
        "semester": 1,
        "subject_id": mock_subject.id
    }
    with pytest.raises(ValidationError):
        AssessmentTemplateCreate(**data)

    data = {
        "name": "15 phút lần 1",
        "type": "test",
        "semester": 1,
        "subject_id": mock_subject.id
    }
    template = AssessmentTemplateCreate(**data)
    assert template.name == data["name"]
    assert template.type == data["type"]
    assert template.semester == data["semester"]
    assert template.subject_id == data["subject_id"]