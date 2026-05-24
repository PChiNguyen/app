from uuid import UUID
from sqlalchemy.orm import Session
from repositories.student_repo import StudentRepository, ReportCardDTO


class GPAService:
    def __init__(self, db: Session):
        self.student_repo = StudentRepository(db)

    def calc_year_avg(self, student_id: UUID) -> float:
        student= self.student_repo.get_by_id(student_id)
        if not student:
            raise ValueError("Không tìm thấy sinh viên với ID này.")  
        hk1_data = self.student_repo.get_student_report_card(student_id, 1)
        hk2_data = self.student_repo.get_student_report_card(student_id, 2)
        if hk1_data is None or hk2_data is None:
            raise ValueError("Không tìm thấy dữ liệu học kỳ cho sinh viên này.")
        hk1_gpa = hk1_data.gpa
        hk2_gpa = hk2_data.gpa

        report_card = ReportCardDTO(
            student_id=student.id,
            student_name=student.name,
            gpa=(hk1_gpa + hk2_gpa) / 2,
            class_rank=0  # Placeholder, as class rank is not calculated here
        )
        return report_card
        
    
 

