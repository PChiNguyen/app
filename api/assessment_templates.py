from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session  
from db.models.user import User 

from api.deps import get_db, get_current_teacher 
from services.assessment_template_service import AssessmentTemplateService  
from schemas.assessment_template_schemas import AssessmentTemplateResponse, AssessmentTemplateCreate, AssessmentTemplateUpdate


router = APIRouter()  


@router.post('/', response_model= AssessmentTemplateResponse, status_code= status.HTTP_201_CREATED)
def create_template(*, db: Session = Depends(get_db),
    current_user: User= Depends(get_current_teacher),
    template_in: AssessmentTemplateCreate):

    service = AssessmentTemplateService(db)
    template = service.create_template(template_in)
    return template 
@router.get('/{template_id}', response_model= AssessmentTemplateResponse)
def get_template_by_id(*, template_id: int, db: Session = Depends(get_db)):
    service = AssessmentTemplateService(db)
    template = service.get_template_by_id(template_id)
    return template 

@router.put('/{template_id}', response_model= AssessmentTemplateResponse)
def update_template(*, template_id: int,
                     db: Session = Depends(get_db),
                     template_in: AssessmentTemplateUpdate):
    service = AssessmentTemplateService(db)
    template = service.update_template(template_id, template_in)
    return template 

@router.delete('/{template_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_template(*, template_id: int,
                     db: Session = Depends(get_db),
                     current_user: User= Depends(get_current_teacher)):
    service = AssessmentTemplateService(db)
    service.delete_template(template_id)
    return




