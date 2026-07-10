from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from schemas.student import ReportCardDTO
from repositories.student_repo import StudentRepository 
from repositories.grading_repo import GradingRepository

class ReportCardService:
    # 1. Set up the workbench once!
    def __init__(self, db: Session):
        self.student_repo = StudentRepository(db)
        self.grading_repo = GradingRepository(db)
    
    # 2. No more @staticmethod. We use 'self' now.
    def get_single_report_card(self, student_id: UUID, semester: int) -> ReportCardDTO:
        # Reach into the workbench to use the repos
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail=f"Student ID {student_id} not found!")

        gpa_record = self.grading_repo.get_student_semester_gpa(student.classroom_id, student.id, semester)

        sem_gpa = gpa_record.semester_gpa if gpa_record else 0.0

        return ReportCardDTO(
            student_id=student.id,
            student_name=student.name, 
            class_rank=None,      
            gpa=sem_gpa                    
        )

    # 3. No more @staticmethod here either.
    def get_batch_report_cards(self, classroom_id: UUID, semester: int) -> list[ReportCardDTO]:
        students = self.student_repo.get_by_classroom_id(classroom_id)
        if not students:
            raise HTTPException(status_code=404, detail="No students found in this classroom!")

        # Just grab the tool from the workbench!
        yearly_gpas = self.grading_repo.get_classroom_semester_gpas(classroom_id, semester)
        
        gpa_map = {record.student_id: record.semester_gpa for record in yearly_gpas}

        report_cards = []
        for s in students:
            report_cards.append(
                ReportCardDTO(
                    student_id=s.id,
                    student_name=s.name,
                    class_rank=None, 
                    gpa=gpa_map.get(s.id, 0.0)
                )
            )
            
        return report_cards