from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session    
from api.deps import get_db, get_current_teacher , get_current_user
from db.models.user import User 
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
@router.put('/{score_id}', response_model=StudentScoreResponse)
def update_score(*, score_id: UUID, db: Session = Depends(get_db), score_in: StudentScoreUpdate):

    service = StudentScoreService(db)
    # 1. Update the score in Postgres (The actual database)
    student_score = service.update_score(score_id, score_in)
    
    # 2. 🔥 THE DETONATOR 🔥
    # (Note: Depending on how your SQLAlchemy models are linked, you might need to adjust 
    # the dot-notation here to get the classroom_id and semester! 
    # Assuming student_score has a link to the student and assessment template...)
    
    try:
        s_id = student_score.student.id # Assuming you have a relationship!
        c_id = student_score.student.classroom_id # Assuming you have a relationship!
        sem = student_score.assessment_template.semester # Assuming you have a relationship!
        
        cache_key = f"gpa:class:{c_id}:student:{s_id}:sem:{sem}"
        
        # Violently rip the sticky note off the whiteboard
        redis_client.delete(cache_key)
        print(f"🔥 BOOM! Deleted stale cache: {cache_key}", flush=True)
        
    except Exception as e:
        # If the relationships aren't loaded, we just print an error but don't crash the API!
        print(f"⚠️ Could not delete cache automatically: {e}", flush=True)

    # 3. Return the updated score to the teacher's screen
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

