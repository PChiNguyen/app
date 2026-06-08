from repositories.grading_repo import GradingRepository 
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID 


class GradingService:
    def __init__(self, db: Session):
        self.grading_repo = GradingRepository(db)

    
    def get_classroom_all_subject_averages_by_semester(self, classroom_id: UUID, semester: int):
        averages = self.grading_repo.get_classroom_all_subject_averages_by_semester(classroom_id, semester)
        if not averages:
            raise HTTPException(status_code=404, detail="No grades found for this classroom and semester")
        return averages

    def get_classroom_semester_gpas(self, classroom_id: UUID, semester: int):
        gpas = self.grading_repo.get_classroom_semester_gpas(classroom_id, semester)
        if not gpas:
            raise HTTPException(status_code=404, detail="No grades found for this classroom and semester")
        return gpas

    def get_classroom_yearly_subject_averages(self, classroom_id: UUID):
        averages = self.grading_repo.get_classroom_yearly_subject_averages(classroom_id)
        if not averages:
            raise HTTPException(status_code=404, detail="No grades found for this classroom")
        return averages

    def get_classroom_yearly_gpas(self, classroom_id: UUID):
        gpas = self.grading_repo.get_classroom_yearly_gpas(classroom_id)
        if not gpas:
            raise HTTPException(status_code=404, detail="No grades found for this classroom")
        return gpas

    def get_student_subject_averages_by_semester(self, classroom_id: UUID, student_id: UUID, semester: int):
        averages = self.grading_repo.get_student_subject_averages_by_semester(classroom_id, student_id, semester)
        if not averages:
            raise HTTPException(status_code=404, detail="No grades found for this student and semester")
        return averages

    def get_student_semester_gpa(self, classroom_id: UUID, student_id: UUID, semester: int):
        gpa = self.grading_repo.get_student_semester_gpa(classroom_id, student_id, semester)
        if not gpa:
            raise HTTPException(status_code=404, detail="No grades found for this student and semester")
        return gpa

    def get_student_yearly_subject_averages(self, classroom_id: UUID, student_id: UUID):
        averages = self.grading_repo.get_student_yearly_subject_averages(classroom_id, student_id)
        if not averages:
            raise HTTPException(status_code=404, detail="No grades found for this student")
        return averages

    def get_student_yearly_gpa(self, classroom_id: UUID, student_id: UUID):
        gpa = self.grading_repo.get_student_yearly_gpa(classroom_id, student_id)
        if not gpa:
            raise HTTPException(status_code=404, detail="No grades found for this student")
        return gpa


        


  