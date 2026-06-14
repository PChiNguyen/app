import pytest 
from db.models.assessment_template import AssessmentTemplate
from db.models.subject import Subject
from repositories.assessment_template_repo import AssessmentTemplateRepository
from schemas.assessment_template_schemas import AssessmentTemplateCreate



def test_create(db_session, mock_subject: Subject):
    repo = AssessmentTemplateRepository(db_session)
    template_in = AssessmentTemplateCreate(subject_id= mock_subject.id, name="hoyeyo", type="midterm", semester=1)
    # ✅ THE FIX: Unpack the Pydantic object into **kwargs!
    new_template: AssessmentTemplate = repo.create(**template_in.model_dump())
    
    assert new_template is not None
    assert new_template.id is not None
    assert new_template.subject_id == template_in.subject_id
    assert new_template.name == template_in.name
    assert new_template.type == template_in.type
    assert new_template.semester == template_in.semester

def test_get_by_id(db_session, mock_assessment_template_semester1: AssessmentTemplate):
    repo = AssessmentTemplateRepository(db_session)
    template = repo.get_by_id(mock_assessment_template_semester1.id)
    
    assert template is not None
    assert template.id == mock_assessment_template_semester1.id
    assert template.subject_id == mock_assessment_template_semester1.subject_id
    assert template.name == mock_assessment_template_semester1.name
    assert template.type == mock_assessment_template_semester1.type
    assert template.semester == mock_assessment_template_semester1.semester

def test_delete(db_session, mock_assessment_template_semester1: AssessmentTemplate):
    repo = AssessmentTemplateRepository(db_session)
    result = repo.delete(mock_assessment_template_semester1.id)
    assert result is True


def test_update(db_session, mock_assessment_template_semester1: AssessmentTemplate):
    repo = AssessmentTemplateRepository(db_session)
    updated_name = "Updated Template Name"
    updated_template = repo.update(mock_assessment_template_semester1.id, name=updated_name)
    assert updated_template.name == updated_name 
    
