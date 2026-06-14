from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_teacher, get_current_user
from services.grading_service import GradingService
from schemas.grading_schemas import (
    SubjectAverageRead, 
    SemesterGPARead, 
    YearlySubjectAverageRead, 
    YearlyGPARead
)

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
    return GradingService(db).get_student_semester_gpa(classroom_id, student_id, semester)

@router.get('/classrooms/{classroom_id}/students/{student_id}/yearly/subject-averages', response_model=List[YearlySubjectAverageRead])
def get_student_yearly_subject_averages(*, classroom_id: UUID, student_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Xem điểm trung bình từng môn CẢ NĂM của một cá nhân học sinh."""
    return GradingService(db).get_student_yearly_subject_averages(classroom_id, student_id)

@router.get('/classrooms/{classroom_id}/students/{student_id}/yearly/gpa', response_model=YearlyGPARead)
def get_student_yearly_gpa(*, classroom_id: UUID, student_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Xem điểm trung bình chung (GPA) CẢ NĂM của một cá nhân học sinh."""
    return GradingService(db).get_student_yearly_gpa(classroom_id, student_id)