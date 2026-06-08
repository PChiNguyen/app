from repositories.student_repo import StudentRepository
from repositories.subject_repo import SubjectRepository
from repositories.classroom_repo import ClassroomRepository
from repositories.student_score_repo import StudentScoreRepository                          
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID



class StudentService:
    def __init__(self, db: Session):
        self.student_repo = StudentRepository(db)
        self.subject_repo = SubjectRepository(db)
        self.classroom_repo = ClassroomRepository(db)
        self.student_score_repo = StudentScoreRepository(db)

    
    def create_student(self, name: str, classroom_id: UUID):
        classroom = self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        return self.student_repo.create(name, classroom_id)
    
    def get_student_by_id(self, student_id: UUID):
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    
    def update_student(self, student_id: UUID, updates: dict):
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        for key, value in updates.items():
            if not hasattr(student, key):
                raise HTTPException(status_code=400, detail=f"Invalid field: {key}")
            if key == "classroom_id":
                classroom = self.classroom_repo.get_by_id(value)
                if not classroom:
                    raise HTTPException(status_code=404, detail="Classroom not found")
        return self.student_repo.update(student_id, **updates)
    
    def delete_student(self, student_id: UUID):
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        if self.student_score_repo.get_by_student_id(student_id):
            raise HTTPException(status_code=400, detail="Cannot delete student with scores")
        return self.student_repo.delete(student_id)
    def list_students_by_classroom(self, classroom_id: UUID):
        classroom = self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        return self.student_repo.get_by_classroom_id(classroom_id)
    def get_multi_students(self, skip: int = 0, limit: int = 100):
        ## no input validations in the service layer !!!, they should be handled in api/routers 
        return self.student_repo.get_multi(skip=skip, limit=limit)
    
    
  