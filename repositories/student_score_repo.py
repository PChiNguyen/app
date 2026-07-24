# repositories/student_score_repo.py
from uuid import UUID 
from typing import Optional   
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore
from core.exceptions import DatabaseValidationError


class StudentScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # 1. THE SYSTEM FUNCTION (Used when a test is announced)
    # ==========================================
    def bulk_create_empty_slots(self, template_id: int, student_ids: list[UUID]) -> list[StudentScore]:
        """
        Creates blank score slots for an entire classroom safely with transaction rollback protection.
        """
        empty_scores = [
            StudentScore(
                student_id=student_id, 
                assessment_template_id=template_id, 
                score=None  # Status will automatically default to PENDING
            ) 
            for student_id in student_ids
        ]
        
        try:
            self.db.add_all(empty_scores)
            self.db.commit()
            for score in empty_scores:
                self.db.refresh(score)
            return empty_scores
        except IntegrityError as e:
            self.db.rollback()  # 🛡️ Reset session if student IDs or template ID do not exist
            raise DatabaseValidationError("Failed to create score slots. Verify student and assessment template IDs.") from e
        except SQLAlchemyError as e:
            self.db.rollback()  # 🛡️ Reset session on general database failure
            raise DatabaseValidationError("A database error occurred while bulk creating empty score slots.") from e

    def create_score(self, **kwargs) -> StudentScore:
        """
        Creates a single score record safely.
        """
        new_score = StudentScore(**kwargs)
        try:
            self.db.add(new_score)
            self.db.commit()
            self.db.refresh(new_score)
            return new_score
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseValidationError("Failed to create score record due to invalid foreign keys or constraints.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while creating the score record.") from e

    # ==========================================
    # 2. THE TEACHER FUNCTION (Used for grading)
    # ==========================================
    def update_score(self, score_id: UUID, **kwargs) -> Optional[StudentScore]:
        """
        Updates an existing student score record safely.
        """
        db_score = self.get_by_id(score_id)
        if not db_score:
            return None
        
        for key, value in kwargs.items():
            if hasattr(db_score, key):
                setattr(db_score, key, value)
            else:
                raise AttributeError(f"StudentScore model has no attribute '{key}'")

        try:
            self.db.commit()
            self.db.refresh(db_score)
            return db_score
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseValidationError("Failed to update score due to invalid data constraints.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while updating the score.") from e

    # ==========================================
    # 3. QUERY & DELETE FUNCTIONS
    # ==========================================
    def get_by_id(self, score_id: UUID) -> Optional[StudentScore]:
        return self.db.query(StudentScore).filter(StudentScore.id == score_id).first()   

    def get_by_student_id(self, student_id: UUID) -> list[StudentScore]:
        return self.db.query(StudentScore).filter(StudentScore.student_id == student_id).all()

    def get_by_template_id(self, template_id: int) -> list[StudentScore]:
        return self.db.query(StudentScore).filter(StudentScore.assessment_template_id == template_id).all()

    def get_by_student_id_and_subject_id(self, student_id: UUID, subject_id: UUID) -> list[StudentScore]:
        return self.db.query(StudentScore).join(AssessmentTemplate).filter(
            StudentScore.student_id == student_id,
            AssessmentTemplate.subject_id == subject_id
        ).all()

    def delete(self, score_id: UUID) -> bool:
        """Physically deletes a student's score from the database safely."""
        score = self.get_by_id(score_id)
        if score:
            try:
                self.db.delete(score)  
                self.db.commit()    
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseValidationError("Failed to delete score record due to database constraints.") from e
        return False