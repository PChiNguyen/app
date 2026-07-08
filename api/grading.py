from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_db, get_current_teacher, get_current_user
from services.grading_service import GradingService
from schemas.grading_schemas import (
    SubjectAverageRead, 
    SemesterGPARead, 
    YearlySubjectAverageRead, 
    YearlyGPARead
)
import redis
import json

# Connect to the Redis container
# Notice the host is 'redis' - Docker automatically routes this to the right room!
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

router = APIRouter()

# ==========================================
# 🏫 CLASSROOM VIEWS (TEACHERS ONLY)
# ==========================================

@router.get('/classrooms/{classroom_id}/semesters/{semester}/subject-averages', response_model=List[SubjectAverageRead])
def get_classroom_subject_averages(*, classroom_id: UUID, semester: int, db: Session = Depends(get_db), current_user = Depends(get_current_teacher)):
    """Thống kê điểm trung bình từng môn của toàn bộ học sinh trong lớp theo học kỳ."""
    return GradingService(db).get_classroom_all_subject_averages_by_semester(classroom_id, semester)

@router.get('/classrooms/{classroom_id}/semesters/{semester}/gpa', response_model=List[SemesterGPARead])
def get_classroom_semester_gpa(*, classroom_id: UUID, semester: int, db: Session = Depends(get_db), current_user = Depends(get_current_teacher)):
    """Thống kê điểm trung bình chung (GPA) của toàn bộ học sinh trong lớp theo học kỳ."""
    return GradingService(db).get_classroom_semester_gpas(classroom_id, semester)

@router.get('/classrooms/{classroom_id}/yearly/subject-averages', response_model=List[YearlySubjectAverageRead])
def get_classroom_yearly_subject_averages(*, classroom_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_teacher)):
    """Thống kê điểm trung bình từng môn CẢ NĂM của toàn bộ học sinh trong lớp."""
    return GradingService(db).get_classroom_yearly_subject_averages(classroom_id)

@router.get('/classrooms/{classroom_id}/yearly/gpa', response_model=List[YearlyGPARead])
def get_classroom_yearly_gpa(*, classroom_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_teacher)):
    """Thống kê điểm trung bình chung (GPA) CẢ NĂM của toàn bộ học sinh trong lớp."""
    return GradingService(db).get_classroom_yearly_gpas(classroom_id)


# ==========================================
# 🎓 INDIVIDUAL STUDENT VIEWS (STUDENTS & TEACHERS)
# ==========================================

@router.get('/classrooms/{classroom_id}/students/{student_id}/semesters/{semester}/subject-averages', response_model=List[SubjectAverageRead])
def get_student_subject_averages(*, classroom_id: UUID, student_id: UUID, semester: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Xem điểm trung bình từng môn của một cá nhân học sinh theo học kỳ."""
    return GradingService(db).get_student_subject_averages_by_semester(classroom_id, student_id, semester)


@router.get('/classrooms/{classroom_id}/students/{student_id}/semesters/{semester}/gpa', response_model=SemesterGPARead)
def get_student_semester_gpa(*, classroom_id: UUID, student_id: UUID, semester: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Xem điểm trung bình chung (GPA) của một cá nhân học sinh theo học kỳ."""
    
    # ==========================================
    # 🛡️ THE RATE LIMITER SHIELD
    # ==========================================
    # 1. Create a unique clipboard for this specific user
    rate_limit_key = f"rate_limit:user:{current_user.id}"
    
    # 2. Add a tally mark to their name (incr automatically creates the key if it doesn't exist)
    request_count = redis_client.incr(rate_limit_key)
    
    # 3. If this is their first tally mark, tell Redis to burn the clipboard after 60 seconds
    if request_count == 1:
        redis_client.expire(rate_limit_key, 60)
        
    # 4. If they have more than 5 tally marks, block them!
    if request_count > 5:
        print(f"🛑 RATE LIMIT TRIGGERED FOR USER {current_user.id}!", flush=True)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bro, slow down! You are spamming the server. Try again in 60 seconds."
        )
    # ==========================================

    # 1. Create a unique sticky-note name (Cache Key) for this exact student's semester
    cache_key = f"gpa:class:{classroom_id}:student:{student_id}:sem:{semester}"
    
    # 2. THE FAST PATH (Check the Redis Whiteboard)
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print("\n⚡ CACHE HIT! Returning instantly from Redis RAM.", flush=True)
        return json.loads(cached_data) # Convert the string back to a Python dictionary
        
    # 3. THE SLOW PATH (Ask Postgres to calculate it)
    print("\n🐢 CACHE MISS! Going down to Postgres to calculate GPA...", flush=True)
    gpa_data = GradingService(db).get_student_semester_gpa(classroom_id, student_id, semester)
    
    # 4. SAVE TO CACHE (Write it on the whiteboard for next time)
    # jsonable_encoder safely converts Pydantic models and UUIDs into standard text so Redis can read it
    redis_client.setex(cache_key, 300, json.dumps(jsonable_encoder(gpa_data))) 
    
    return gpa_data

@router.get('/classrooms/{classroom_id}/students/{student_id}/yearly/subject-averages', response_model=List[YearlySubjectAverageRead])
def get_student_yearly_subject_averages(*, classroom_id: UUID, student_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Xem điểm trung bình từng môn CẢ NĂM của một cá nhân học sinh."""
    return GradingService(db).get_student_yearly_subject_averages(classroom_id, student_id)

@router.get('/classrooms/{classroom_id}/students/{student_id}/yearly/gpa', response_model=YearlyGPARead)
def get_student_yearly_gpa(*, classroom_id: UUID, student_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Xem điểm trung bình chung (GPA) CẢ NĂM của một cá nhân học sinh."""
    return GradingService(db).get_student_yearly_gpa(classroom_id, student_id)