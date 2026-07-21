from repositories.assessment_template_repo import AssessmentTemplateRepository
from repositories.student_score_repo import StudentScoreRepository
from repositories.subject_repo import SubjectRepository

from schemas.assessment_template_schemas import AssessmentTemplateCreate, AssessmentTemplateUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException

class AssessmentTemplateService:
    def __init__(self, db: Session): 
        self.template_repo = AssessmentTemplateRepository(db)
        self.score_repo = StudentScoreRepository(db)
        self.subject_repo = SubjectRepository(db)
    
    def create_template(self, template_in: AssessmentTemplateCreate):
        subject = self.subject_repo.get_by_id(template_in.subject_id)
        if not subject:
            raise HTTPException(
                status_code=404, 
                detail=f"Subject with ID {template_in.subject_id} not found."
            )
        
        return self.template_repo.create(**template_in.model_dump())
        
    
    def get_template_by_id(self, template_id: int):
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found")
        return template
        
    def update_template(self, template_id: int, template_in: AssessmentTemplateUpdate):
            # 1. Bouncer Check: Does the template even exist?
            template = self.template_repo.get_by_id(template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")

            # 2. Convert the Pydantic schema to a raw Python dictionary
            updates = template_in.model_dump(exclude_unset=True)

            # 🚨 THE BOUNCER BLOCK: Guard the subject identity!
            
        

            # 3. Safe to pass the remaining clean updates to the repository
            return self.template_repo.update(template_id, **updates)
    def delete_template(self, template_id: int):
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        if self.score_repo.get_by_template_id(template_id):
            raise HTTPException(status_code=400, detail="Cannot delete template with associated scores")
        return self.template_repo.delete(template_id)
    
    
        
    
