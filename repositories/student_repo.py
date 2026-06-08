from dataclasses import dataclass
from uuid import UUID 
from typing import List, Optional  
from sqlalchemy.orm import Session  
from db.models.student import Student 

# This tells VS Code exactly what the report card data shape looks like!
@dataclass 
class ReportCardDTO:
    student_id: UUID
    student_name: str
    gpa: float
    class_rank: int

class StudentRepository: 
    def __init__(self, db: Session):
        self.db = db 

    def create(self, name: str, classroom_id: UUID) -> Student:
        new_student = Student(name=name, classroom_id=classroom_id)
        self.db.add(new_student)
        self.db.commit()
        self.db.refresh(new_student)
        return new_student  

    def delete(self, student_id: UUID) -> bool:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if student:
            self.db.delete(student)
            self.db.commit()    
            return True 
        return False 

    def get_by_id(self, student_id: UUID) -> Optional[Student]:
        return self.db.query(Student).filter(Student.id == student_id).first()

    def get_by_classroom_id(self, classroom_id: UUID) -> List[Student]:
        return self.db.query(Student).filter(Student.classroom_id == classroom_id).all()

    def update(self, student_id: UUID, **kwargs) -> Optional[Student]:
        student = self.get_by_id(student_id)
        if not student:
            return None
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
            else:
                raise AttributeError(f"Student model has no attribute '{key}'")
        self.db.commit()
        self.db.refresh(student)   
        return student 
    
    def get_multi(self, skip: int = 0, limit: int = 100):
        # Pagination to ensure performance scales gracefully
        return self.db.query(Student).offset(skip).limit(limit).all()

    def count_by_ids(self, student_ids: List[UUID]) -> int:
        """Counts how many of the provided IDs actually exist in the DB."""
        if not student_ids:
            return 0
        return self.db.query(Student).filter(Student.id.in_(student_ids)).count()