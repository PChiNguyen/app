from multiprocessing import Value

from repositories.classroom_repo import ClassroomRepository 
from repositories.user_repo import UserRepository 
from repositories.student_repo import StudentRepository 
from fastapi import HTTPException 

from sqlalchemy.orm import Session
from uuid import UUID 

class ClassroomService:
    def __init__(self, db: Session):
        self.classroom_repo = ClassroomRepository(db)
        self.user_repo = UserRepository(db)
        self.student_repo = StudentRepository(db)

    
    def create_classroom(self, name: str, teacher_id: UUID):
        if not self.user_repo.get_by_id(teacher_id):
            raise HTTPException(status_code=404, detail="Teacher not found")
        return self.classroom_repo.create(name, teacher_id)
    
    def get_classroom(self, classroom_id: UUID):
        classroom = self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            raise HTTPException(status_code=404, detail="Classroom not found")
        return classroom
        
    def update_classroom(self, classroom_id: UUID, updates: dict):
            # 1. Bouncer Check 1: Does it exist?
            classroom = self.classroom_repo.get_by_id(classroom_id)
            if not classroom:
                raise HTTPException(status_code=404, detail="Classroom not found")
                
            ## let schema do the validation please 
                    
            return self.classroom_repo.update(classroom_id, **updates)
    def delete_classroom(self, classroom_id: UUID):
        if not self.classroom_repo.get_by_id(classroom_id):
            raise HTTPException(status_code=404, detail="Classroom not found")
        if self.student_repo.get_by_classroom_id(classroom_id):
            raise HTTPException(status_code=400, detail="Cannot delete classroom with students")
        return self.classroom_repo.delete(classroom_id)
    def list_classrooms(self, teacher_id: UUID):
        if not self.user_repo.get_by_id(teacher_id):
            raise HTTPException(status_code=404, detail="Teacher not found")
        return self.classroom_repo.get_by_teacher_id(teacher_id)
    


    def list_all_classrooms(self, skip: int = 0, limit: int = 100):
        ## the validation should be in the api/routers layer, not here in the service layer 

        return self.classroom_repo.get_multi(skip=skip, limit=limit)
    
    
  
    
