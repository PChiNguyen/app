# repositories/classroom_repo.py
from uuid import UUID 
from typing import List, Optional, NamedTuple   
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.models.classroom import Classroom
from core.exceptions import DatabaseValidationError


class LeaderboardRow(NamedTuple): 
    student_id: UUID
    student_name: str
    gpa: float
    class_rank: int


class ClassroomRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, teacher_id: UUID) -> Classroom:
        """
        Creates a new classroom safely with transaction rollback protection.
        """
        new_classroom = Classroom(name=name, teacher_id=teacher_id)
        try:
            self.db.add(new_classroom)
            self.db.commit()
            self.db.refresh(new_classroom)
            return new_classroom
        except IntegrityError as e:
            self.db.rollback()  # 🛡️ Reset session on constraint failure (e.g. invalid teacher_id)
            raise DatabaseValidationError("Failed to create classroom. Verify that the teacher ID is valid.") from e
        except SQLAlchemyError as e:
            self.db.rollback()  # 🛡️ Reset session on general database failure
            raise DatabaseValidationError("A database error occurred while creating the classroom.") from e

    def update(self, classroom_id: UUID, **kwargs) -> Optional[Classroom]:
        """
        Updates classroom attributes dynamically with transaction safety.
        """
        classroom = self.get_by_id(classroom_id)
        if not classroom:
            return None

        for key, value in kwargs.items():
            if hasattr(classroom, key):
                setattr(classroom, key, value)
            else:
                raise AttributeError(f"Classroom model has no attribute '{key}'")

        try:
            self.db.commit()
            self.db.refresh(classroom)   
            return classroom
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseValidationError("Failed to update classroom due to database constraints.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while updating the classroom.") from e

    def delete(self, classroom_id: UUID) -> bool:
        """
        Deletes a classroom with transaction rollback safety.
        """
        classroom = self.get_by_id(classroom_id)
        if classroom:
            try:
                self.db.delete(classroom)  
                self.db.commit()    
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseValidationError("Failed to delete classroom. Ensure dependent students are removed first.") from e
        return False

    def get_by_id(self, classroom_id: UUID) -> Optional[Classroom]:
        """Fetches a single classroom by ID. Read-only."""
        return self.db.query(Classroom).filter(Classroom.id == classroom_id).first()

    def get_by_teacher_id(self, teacher_id: UUID) -> List[Classroom]:
        """Fetches all classrooms assigned to a specific teacher. Read-only."""
        return self.db.query(Classroom).filter(Classroom.teacher_id == teacher_id).all()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Classroom]:
        """
        Pagination query to return classrooms in manageable batches. Read-only.
        """
        return self.db.query(Classroom).offset(skip).limit(limit).all()