from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_db, get_current_teacher, get_current_user
from db.models.user import User
from services.grading_service import GradingService
from schemas.grading_schemas import (
    SubjectAverageRead, 
    SemesterGPARead, 
    YearlySubjectAverageRead, 
    YearlyGPARead
)
from services.gpa_caching_service import GPACachingService
from core.rate_limiter import RateLimiter 
from core.redis import get_redis_client
from repositories.grading_repo import GradingRepository 
import redis
import json
import os 



router = APIRouter()

# ==========================================
# 🏫 CLASSROOM VIEWS (TEACHERS ONLY)
# ==========================================

@router.get('/classrooms/{classroom_id}/semesters/{semester}/subject-averages', response_model=List[SubjectAverageRead])
def get_classroom_subject_averages(*, classroom_id: UUID, semester: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher)):
    """Thống kê điểm trung bình từng môn của toàn bộ học sinh trong lớp theo học kỳ."""
    return GradingService(db).get_classroom_all_subject_averages_by_semester(classroom_id, semester)

@router.get('/classrooms/{classroom_id}/semesters/{semester}/gpa', response_model=List[SemesterGPARead])
def get_classroom_semester_gpa(*, classroom_id: UUID, semester: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher)):
    """Thống kê điểm trung bình chung (GPA) của toàn bộ học sinh trong lớp theo học kỳ."""
    return GradingService(db).get_classroom_semester_gpas(classroom_id, semester)

@router.get('/classrooms/{classroom_id}/yearly/subject-averages', response_model=List[YearlySubjectAverageRead])
def get_classroom_yearly_subject_averages(*, classroom_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher)):
    """Thống kê điểm trung bình từng môn CẢ NĂM của toàn bộ học sinh trong lớp."""
    return GradingService(db).get_classroom_yearly_subject_averages(classroom_id)

@router.get('/classrooms/{classroom_id}/yearly/gpa', response_model=List[YearlyGPARead])
def get_classroom_yearly_gpa(*, classroom_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_teacher)):
    """Thống kê điểm trung bình chung (GPA) CẢ NĂM của toàn bộ học sinh trong lớp."""
    return GradingService(db).get_classroom_yearly_gpas(classroom_id)


# ==========================================
# 🎓 INDIVIDUAL STUDENT VIEWS (STUDENTS & TEACHERS)
# ==========================================

@router.get('/classrooms/{classroom_id}/students/{student_id}/semesters/{semester}/subject-averages', response_model=List[SubjectAverageRead])
def get_student_subject_averages(*, classroom_id: UUID, student_id: UUID, semester: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Xem điểm trung bình từng môn của một cá nhân học sinh theo học kỳ."""
    return GradingService(db).get_student_subject_averages_by_semester(classroom_id, student_id, semester)

@router.get(
    "/classroom/{classroom_id}/student/{student_id}/semester/{semester}/gpa",
    response_model=SemesterGPARead,
    dependencies=[Depends(RateLimiter(requests_limit=5, window_seconds=60))]
)
def get_student_semester_gpa(
    classroom_id: UUID,
    student_id: UUID,
    semester: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xem điểm GPA học kỳ của học sinh (Tự động Cache bằng Decorator trong Repository)."""
    repo = GradingRepository(db)
    gpa_data = repo.get_student_semester_gpa(classroom_id, student_id, semester)
    
    if not gpa_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student GPA record not found for this semester."
        )
        
    return gpa_data

@router.get('/classrooms/{classroom_id}/students/{student_id}/yearly/subject-averages', response_model=List[YearlySubjectAverageRead])
def get_student_yearly_subject_averages(*, classroom_id: UUID, student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Xem điểm trung bình từng môn CẢ NĂM của một cá nhân học sinh."""
    return GradingService(db).get_student_yearly_subject_averages(classroom_id, student_id)

@router.get('/classrooms/{classroom_id}/students/{student_id}/yearly/gpa', response_model=YearlyGPARead)
def get_student_yearly_gpa(*, classroom_id: UUID, student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Xem điểm trung bình chung (GPA) CẢ NĂM của một cá nhân học sinh."""
    return GradingService(db).get_student_yearly_gpa(classroom_id, student_id)