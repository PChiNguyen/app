from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_teacher
from schemas.student import StudentRead, StudentCreate, StudentUpdate
from services.student_service import StudentService # ✅ The real brain imported!
from services.report_card_service import ReportCardService 





from fastapi import APIRouter, Response
# Make sure your imports match your folder structure!
from schemas.student import ReportCardDTO 
from infras.exporters import FileExporter
import uuid





router = APIRouter() 

@router.post('/', response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(*, 
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_teacher),
                   student_in: StudentCreate):
    # Pass the Pydantic box straight down. No unpacking here!
    return StudentService(db).create_student(student_in.name, student_in.classroom_id)

@router.get('/', response_model=List[StudentRead])
def read_students(*, 
                  skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db),
                  current_user = Depends(get_current_teacher)):
    return StudentService(db).get_multi_students(skip=skip, limit=limit) 

@router.get('/{student_id}', response_model=StudentRead)
def read_student(*, 
                 student_id: UUID,
                 db: Session = Depends(get_db),
                 current_user = Depends(get_current_teacher)):
    # The service raises the 404 error if missing. We just return!
    return StudentService(db).get_student_by_id(student_id)

@router.put('/{student_id}', response_model=StudentRead)
def update_student(*, 
                   student_id: UUID,
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_teacher),
                   student_in: StudentUpdate):
    # No .model_dump() needed! The service handles the exclude_unset logic.
    return StudentService(db).update_student(student_id, student_in)

@router.delete('/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student(*, 
                   student_id: UUID,
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_teacher)):
    # The service runs all safety checks before deleting.
    StudentService(db).delete_student(student_id)
    return None





### Nghịch 


# 1. Added {classroom_id} to the path!
@router.get("/export/classrooms/{classroom_id}/csv")
def download_csv(classroom_id: uuid.UUID, semester: int, db: Session = Depends(get_db)):
    # Instantiate the service with the DB session first
    report_service = ReportCardService(db)
    real_data = report_service.get_batch_report_cards(classroom_id, semester)

    csv_bytes = FileExporter.generate_reportcard_csv(real_data)

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="official_report_cards.csv"'}
    )

@router.get("/export/classrooms/{classroom_id}/attendance/txt")
def download_txt(classroom_id: uuid.UUID, semester: int, db: Session = Depends(get_db)):
    report_service = ReportCardService(db)
    real_data: List[ReportCardDTO] = report_service.get_batch_report_cards(classroom_id, semester)
    
    student_names = [student.student_name for student in real_data]
    txt_bytes = FileExporter.generate_student_roster_txt(student_names)

    return Response(
        content=txt_bytes,
        media_type="text/plain", 
        headers={"Content-Disposition": 'attachment; filename="class_attendance_roster.txt"'}
    )

@router.get("/export/students/{student_id}/pdf")
def download_single_pdf(student_id: uuid.UUID, semester: int, db: Session = Depends(get_db)):
    report_service = ReportCardService(db)
    real_student = report_service.get_single_report_card(student_id, semester)

    pdf_bytes = FileExporter.generate_report_card_pdf(real_student)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="report_card_{student_id}.pdf"'}
    )

@router.get("/export/classrooms/{classroom_id}/batch-pdf")
def download_batch_pdf(classroom_id: uuid.UUID, semester: int, db: Session = Depends(get_db)):
    report_service = ReportCardService(db)
    real_data = report_service.get_batch_report_cards(classroom_id, semester)

    pdf_bytes = FileExporter.generate_batch_report_cards_pdf(real_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="classroom_{classroom_id}_report_cards.pdf"'}
    )