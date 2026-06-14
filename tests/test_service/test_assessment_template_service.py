from services.assessment_template_service import AssessmentTemplateService  
from db.models.assessment_template import AssessmentTemplate 
from schemas.assessment_template_schemas import AssessmentTemplateCreate, AssessmentTemplateUpdate
from db.models.student_score import StudentScore 
from db.models.subject import Subject 
from fastapi import HTTPException
from sqlalchemy.orm import Session 
import pytest 
from uuid import uuid4 

def test_get_template_by_inexistent_id(db_session: Session):
    with pytest.raises(HTTPException):
        AssessmentTemplateService(db_session).get_template_by_id(uuid4()) 

def test_delete_template_with_scores(db_session: Session, mock_assessment_template_semester1: AssessmentTemplate, mock_student_score_semester1: StudentScore):
    with pytest.raises(HTTPException):
        AssessmentTemplateService(db_session).delete_template(mock_assessment_template_semester1.id)




# test_assessment_template_service.py

def test_create_template_success(db_session, mock_subject: Subject):
    service = AssessmentTemplateService(db_session)
    # We use the Pydantic schema here as expected by your service
    template_in = AssessmentTemplateCreate(
        subject_id=mock_subject.id, 
        name="15 Minute Quiz", 
        type="test", 
        semester=1
    )
    new_template = service.create_template(template_in)
    assert new_template is not None
    assert new_template.name == "15 Minute Quiz"
    assert new_template.subject_id == mock_subject.id

def test_get_template_by_id_success(db_session, mock_assessment_template_semester1: AssessmentTemplate):
    service = AssessmentTemplateService(db_session)
    template = service.get_template_by_id(mock_assessment_template_semester1.id)
    assert template.name == "Math Test"

def test_update_template_success(db_session, mock_assessment_template_semester1: AssessmentTemplate):
    service = AssessmentTemplateService(db_session)
    # Using the update schema
    update_data = AssessmentTemplateUpdate(name="Updated Math Final")
    updated = service.update_template(mock_assessment_template_semester1.id, update_data)
    assert updated.name == "Updated Math Final"

def test_delete_template_success(db_session, mock_subject: Subject):
    service = AssessmentTemplateService(db_session)
    # 1. Create a fresh template with NO scores attached
    template_in = AssessmentTemplateCreate(subject_id=mock_subject.id, name="Temp", type="test", semester=1)
    temp_template = service.create_template(template_in)
    
    # 2. Safely delete it
    result = service.delete_template(temp_template.id)
    assert result is True