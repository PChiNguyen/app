from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session    
from api.deps import get_db, get_current_teacher   
from db.models.user import User 
from services.student_score_service import StudentScoreService 

from schemas.student_score_schemas import StudentScoreUpdate, StudentScoreResponse, StudentScoreCreate


router = APIRouter()   


@router.post('/', response_model= StudentScoreResponse, status_code= status.HTTP_201_CREATED)
def create_student_score(*, db: Session = Depends(get_db),
                          current_user: User= Depends(get_current_teacher),
                            student_score_in: StudentScoreCreate):
    
    service = StudentScoreService(db)
    student_score = service.create_score(student_score_in)
    return student_score 


@router.get('/', response_model= List[StudentScoreResponse])
def read_scores_by_student_id(*, student_id: UUID,
                               db: Session = Depends(get_db)):
    service = StudentScoreService(db)
    scores = service.get_scores_by_student_id(student_id)
    return scores 

@router.get('/template/{template_id}', response_model= List[StudentScoreResponse])
def read_scores_by_template_id(*, template_id: int, db: Session = Depends(get_db)):
    service = StudentScoreService(db)
    scores = service.get_scores_by_template_id(template_id)
    return scores 

@router.get('/student/{student_id}/subject/{subject_id}', response_model= List[StudentScoreResponse])
def read_scores_by_student_id_and_subject_id(*, student_id: UUID, subject_id: int, db: Session = Depends(get_db)):
    service = StudentScoreService(db)
    scores = service.get_scores_by_student_id_and_subject_id(student_id, subject_id)
    return scores

@router.put('/{score_id}', response_model= StudentScoreResponse)
def update_score(*, score_id: UUID,
                  db: Session = Depends(get_db),
                    score_in: StudentScoreUpdate):

    service = StudentScoreService(db)
    student_score = service.update_score(score_id, score_in)
    return student_score 

@router.delete('/{score_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student_score(*, 
                         score_id: UUID,
                         db: Session = Depends(get_db),
                         current_user = Depends(get_current_teacher)):
    """
    Deletes a specific score entry.
    Requires Teacher or Admin privileges.
    """
    service = StudentScoreService(db) 
    
    # The service automatically raises a 404 if the score is missing!
    service.delete_score(score_id)
    
    return None

