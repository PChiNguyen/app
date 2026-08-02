from uuid import UUID
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_teacher, get_current_user
from db.models.user import User
from schemas.grading_schemas import (
    SubjectAverageRead, 
    SemesterGPARead, 
    YearlySubjectAverageRead, 
    YearlyGPARead
)
from core.rate_limiter import RateLimiter 
from repositories.grading_repo import GradingRepository
from workers.tasks import calculate_classroom_semester_gpas_task  
from celery.result import AsyncResult

router = APIRouter()

# ==========================================
# 🛠️ DRY HELPER FUNCTION (XỬ LÝ LỖI DÙNG CHUNG)
# ==========================================
def get_or_404(data: Any, detail: str = "Resource not found") -> Any:
    """
    Hàm tiện ích kiểm tra dữ liệu: 
    Nếu data rỗng (None hoặc []), tự động bắn lỗi HTTP 404.
    """
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=detail
        )
    return data


# ==========================================
# 🏫 CLASSROOM VIEWS (TEACHERS ONLY)
# ==========================================

@router.get(
    '/classrooms/{classroom_id}/semesters/{semester}/subject-averages', 
    response_model=List[SubjectAverageRead],
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_classroom_subject_averages(
    classroom_id: UUID, 
    semester: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_teacher)
):
    """Thống kê điểm trung bình từng môn của toàn bộ học sinh trong lớp theo học kỳ."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_classroom_all_subject_averages_by_semester(classroom_id, semester),
        detail="No subject averages found for this classroom in the given semester."
    )

@router.get(
    '/classrooms/{classroom_id}/semesters/{semester}/gpa', 
    response_model=List[SemesterGPARead],
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_classroom_semester_gpa(
    classroom_id: UUID, 
    semester: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_teacher)
):
    """Thống kê điểm trung bình chung (GPA) của toàn bộ học sinh trong lớp theo học kỳ."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_classroom_semester_gpas(classroom_id, semester),
        detail="No GPA records found for this classroom in the given semester."
    )

@router.get(
    '/classrooms/{classroom_id}/yearly/subject-averages', 
    response_model=List[YearlySubjectAverageRead],
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_classroom_yearly_subject_averages(
    classroom_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_teacher)
):
    """Thống kê điểm trung bình từng môn CẢ NĂM của toàn bộ học sinh trong lớp."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_classroom_yearly_subject_averages(classroom_id),
        detail="No yearly subject averages found for this classroom."
    )

@router.get(
    '/classrooms/{classroom_id}/yearly/gpa', 
    response_model=List[YearlyGPARead],
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_classroom_yearly_gpa(
    classroom_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_teacher)
):
    """Thống kê điểm trung bình chung (GPA) CẢ NĂM của toàn bộ học sinh trong lớp."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_classroom_yearly_gpas(classroom_id),
        detail="No yearly GPA records found for this classroom."
    )


# ==========================================
# 🎓 INDIVIDUAL STUDENT VIEWS (STUDENTS & TEACHERS)
# ==========================================

@router.get(
    '/classrooms/{classroom_id}/students/{student_id}/semesters/{semester}/subject-averages', 
    response_model=List[SubjectAverageRead],
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_student_subject_averages(
    classroom_id: UUID, 
    student_id: UUID, 
    semester: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Xem điểm trung bình từng môn của một cá nhân học sinh theo học kỳ."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_student_subject_averages_by_semester(classroom_id, student_id, semester),
        detail="Student subject averages not found for this semester."
    )

@router.get(
    "/classroom/{classroom_id}/student/{student_id}/semester/{semester}/gpa",
    response_model=SemesterGPARead,
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_student_semester_gpa(
    classroom_id: UUID, 
    student_id: UUID, 
    semester: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Xem điểm GPA học kỳ của học sinh (Tự động Cache bằng Decorator)."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_student_semester_gpa(classroom_id, student_id, semester),
        detail="Student GPA record not found for this semester."
    )

@router.get(
    '/classrooms/{classroom_id}/students/{student_id}/yearly/subject-averages', 
    response_model=List[YearlySubjectAverageRead],
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_student_yearly_subject_averages(
    classroom_id: UUID, 
    student_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Xem điểm trung bình từng môn CẢ NĂM của một cá nhân học sinh."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_student_yearly_subject_averages(classroom_id, student_id),
        detail="Student yearly subject averages not found."
    )

@router.get(
    '/classrooms/{classroom_id}/students/{student_id}/yearly/gpa', 
    response_model=YearlyGPARead,
    dependencies=[Depends(RateLimiter(requests_limit=3, window_seconds=20))]
)
def get_student_yearly_gpa(
    classroom_id: UUID, 
    student_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Xem điểm trung bình chung (GPA) CẢ NĂM của một cá nhân học sinh."""
    repo = GradingRepository(db)
    return get_or_404(
        repo.get_student_yearly_gpa(classroom_id, student_id),
        detail="Student yearly GPA record not found."
    )



## redis shit 
@router.post("/classroom/{classroom_id}/calculate-semestral-gpa", status_code=status.HTTP_202_ACCEPTED)
def trigger_classroom_semester_gpa_calculation(classroom_id: UUID, semester: int):
    """
    Triggers heavy classroom GPA calculation asynchronously.
    Returns HTTP 202 Accepted immediately with a task_id.
    """
    classroom_id_str = str(classroom_id)

    # Dispatch task to Celery worker via Redis
    task = calculate_classroom_semester_gpas_task.delay(classroom_id_str, semester)

    return {
        "message": "Classroom semester GPA calculation job queued successfully.",
        "task_id": task.id,
        "status": "PENDING"
    }


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """
    Checks the status and result of a background Celery task.
    """
    task_result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.status
    }

    if task_result.ready():
        if task_result.successful():
            response["result"] = task_result.result
        else:
            response["error"] = str(task_result.info)

    return response