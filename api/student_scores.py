from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session    
from api.deps import get_db, get_current_teacher , get_current_user
from db.models.user import User 
from repositories.student_score_repo import StudentScoreRepository
from services.student_score_service import StudentScoreService 
import redis  
import os 

from schemas.student_score_schemas import StudentScoreUpdate, StudentScoreResponse, StudentScoreCreate


router = APIRouter()   


@router.post('/', response_model= StudentScoreResponse, status_code= status.HTTP_201_CREATED)
def create_student_score(*, db: Session = Depends(get_db),
                          current_user: User= Depends(get_current_teacher),
                            student_score_in: StudentScoreCreate):
    
    service = StudentScoreService(db)
    student_score = service.create_score(student_score_in)
    return student_score 


# app/api/routers/student_scores.py
@router.get('/student/{student_id}', response_model=List[StudentScoreResponse])
def read_scores_by_student_id(*, 
                              student_id: UUID,
                              db: Session = Depends(get_db),
                              current_user = Depends(get_current_user)): # 🔒 SECURITY LOCK ADDED
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



# =============================================================================
# 🔌 DYNAMIC REDIS CONNECTION (Works on GitHub & Render)
# =============================================================================
# 1. Look for Render's environment variable. 
# 2. If missing, fall back to 'redis://redis:6379' which matches your GitHub ci.yml!
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Initialize the client using the complete URL string
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# ... (keep your other routes the same) ...

# 2. UPDATE YOUR PUT ENDPOINT
@router.put(
    "/{score_id}", 
    response_model=StudentScoreResponse,
    status_code=status.HTTP_200_OK
)
def update_score(
    score_id: UUID, 
    score_in: StudentScoreUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher)
):
    """
    API Endpoint: Cập nhật điểm số học sinh.
    Tự động xóa sạch Cache GPA trong Redis thông qua Decorator ở Service layer!
    """
    score_repo = StudentScoreRepository(db)
    service = StudentScoreService(score_repo)
    
    return service.update_score(score_id, score_in)
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

