# repositories/subject_repo.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.models.subject import Subject
from core.exceptions import DatabaseValidationError


class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str) -> Subject:
        """
        Creates a new school Subject safely with transaction rollback protection.
        
        Args:
            name (str): The official name of the subject (e.g., 'Mathematics').
        """
        new_subject = Subject(name=name)
        try:
            self.db.add(new_subject)
            self.db.commit()
            self.db.refresh(new_subject)
            return new_subject
        except IntegrityError as e:
            self.db.rollback()  # 🛡️ Reset session if subject name already exists
            raise DatabaseValidationError(f"A subject named '{name}' already exists.") from e
        except SQLAlchemyError as e:
            self.db.rollback()  # 🛡️ Reset session on database operation failure
            raise DatabaseValidationError("A database error occurred while creating the subject.") from e

    def get_all(self) -> list[Subject]:
        """
        Retrieves all subject records. Read-only.
        """
        return self.db.query(Subject).all()

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        """
        Retrieves a single subject by its primary key ID. Read-only.
        """
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_by_name(self, name: str) -> Optional[Subject]:
        """
        Retrieves a single subject by its exact name. Read-only.
        """
        return self.db.query(Subject).filter(Subject.name == name).first()