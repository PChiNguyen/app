from repositories.student_repo import StudentRepository
from repositories.subject_repo import SubjectRepository
from repositories.classroom_repo import ClassroomRepository
from repositories.student_score_repo import StudentScoreRepository                          
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from schemas.student import StudentUpdate



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
    
    def update_student(self, student_id: UUID, updates_in: StudentUpdate):
        """
        Safely handles partial updates for students.
        Validates the relational database links completely inside the Service layer.
        """
        # 1. BOUNCER CHECK: Does the student exist?
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # 2. TRANSFORM: Convert the Pydantic data contract into a raw dictionary
        # exclude_unset=True guarantees we ignore any fields the teacher didn't change!
        updates = updates_in.model_dump(exclude_unset=True)
        
        # 3. BUSINESS RULES: If they are moving classrooms, verify the new class exists!
        for key, value in updates.items():
            if key == "classroom_id" and value is not None:
                classroom = self.classroom_repo.get_by_id(value)
                if not classroom:
                    raise HTTPException(status_code=404, detail="Classroom not found")
            
        # 4. EXECUTE: Pass the clean dictionary unpack straight down to the repository layer
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
    
    
    
  