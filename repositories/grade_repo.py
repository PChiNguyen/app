from uuid import UUID 
from db.models.grade import Grade
from sqlalchemy.orm import Session
from typing import List, Optional     
from db.models.grade import SubjectCoefficient 

class GradeRepository:
    def __init__(self, db: Session):
        self.db = db
    def create(self, subject: str, score: float, student_id: UUID, coefficient: SubjectCoefficient= SubjectCoefficient.TESTS) -> Grade:
        new_grade = Grade(subject=subject, score=score, student_id=student_id, coefficient=coefficient)
        self.db.add(new_grade)
        self.db.commit()
        self.db.refresh(new_grade)
        return new_grade
    def delete(self, grade_id: UUID) -> bool:
        grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if grade:
            self.db.delete(grade)
            self.db.commit()    
            return True 
        return False
    def get_by_id(self, grade_id: UUID) -> Optional[Grade]:
        return self.db.query(Grade).filter(Grade.id == grade_id).first()    
    def get_by_student_id(self, student_id: UUID) -> List[Grade]:
        return self.db.query(Grade).filter(Grade.student_id == student_id).all()
    def update(self, grade_id: UUID, **kwargs) -> Optional[Grade]:
        grade = self.get_by_id(grade_id)
        if not grade:
            return None
        for key, value in kwargs.items():
            if hasattr(grade, key):
                setattr(grade, key, value)
            else:
                # Now it will raise the error your test is looking for!
                raise AttributeError(f"Grade model has no attribute '{key}'")
        self.db.commit()
        self.db.refresh(grade)   
        return grade
    def get_multi_by_subject(self, subject: str, skip: int = 0, limit: int = 100):
        return self.db.query(Grade).filter(Grade.subject == subject).offset(skip).limit(limit).all()
    