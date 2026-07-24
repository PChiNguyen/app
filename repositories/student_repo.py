# repositories/student_repo.py
from dataclasses import dataclass
from uuid import UUID 
from typing import List, Optional  
from sqlalchemy.orm import Session  
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.models.student import Student 
from core.exceptions import DatabaseValidationError


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
        """Creates a new student record with transaction rollback protection."""
        new_student = Student(name=name, classroom_id=classroom_id)
        try:
            self.db.add(new_student)
            self.db.commit()
            self.db.refresh(new_student)
            return new_student  
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseValidationError("Failed to create student. Please verify the classroom ID.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while creating the student record.") from e

    def update(self, student_id: UUID, **kwargs) -> Optional[Student]:
        """Updates student attributes safely."""
        student = self.get_by_id(student_id)
        if not student:
            return None

        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
            else:
                raise AttributeError(f"Student model has no attribute '{key}'")

        try:
            self.db.commit()
            self.db.refresh(student)   
            return student
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseValidationError("Failed to update student profile due to data conflict.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while updating the student record.") from e

    def delete(self, student_id: UUID) -> bool:
        """Deletes a student record with transaction rollback protection."""
        student = self.get_by_id(student_id)
        if student:
            try:
                self.db.delete(student)
                self.db.commit()    
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseValidationError("Failed to delete student record. Ensure dependent scores are removed first.") from e
        return False 

    def get_by_id(self, student_id: UUID) -> Optional[Student]:
        return self.db.query(Student).filter(Student.id == student_id).first()

    def get_by_classroom_id(self, classroom_id: UUID) -> List[Student]:
        return self.db.query(Student).filter(Student.classroom_id == classroom_id).all()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Student]:
        # Pagination to ensure performance scales gracefully
        return self.db.query(Student).offset(skip).limit(limit).all()

    def count_by_ids(self, student_ids: List[UUID]) -> int:
        """Counts how many of the provided IDs actually exist in the DB."""
        if not student_ids:
            return 0
        return self.db.query(Student).filter(Student.id.in_(student_ids)).count()