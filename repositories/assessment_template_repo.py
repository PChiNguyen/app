from uuid import UUID 
from sqlalchemy import func 
from db.models.assessment_template import AssessmentTemplate
from sqlalchemy.orm import Session
from typing import Optional   


class AssessmentTemplateRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self,subject_id: int, name: str, type: str, semester: int) -> AssessmentTemplate:
        new_template = AssessmentTemplate(subject_id=subject_id, name=name, type=type, semester=semester)
        self.db.add(new_template)
        self.db.commit()
        self.db.refresh(new_template)
        return new_template
    def delete(self, template_id: int) -> bool:
        template = self.db.query(AssessmentTemplate).filter(AssessmentTemplate.id == template_id).first()
        if template:
            self.db.delete(template)
            self.db.commit()
            return True
        return False
    def update(self, template_id: int, **kwargs) -> Optional[AssessmentTemplate]:
        template = self.get_by_id(template_id)
        if not template:
            return None
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
            else:
                raise AttributeError(f"AssessmentTemplate model has no attribute '{key}'")
        self.db.commit()
        self.db.refresh(template)
        return template
    

    def get_by_id(self, template_id: int) -> Optional[AssessmentTemplate]:
        return self.db.query(AssessmentTemplate).filter(AssessmentTemplate.id == template_id).first()