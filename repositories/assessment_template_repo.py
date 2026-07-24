# repositories/assessment_template_repo.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.models.assessment_template import AssessmentTemplate
from core.exceptions import DatabaseValidationError


class AssessmentTemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> AssessmentTemplate:
        """
        Creates an assessment template safely with transaction rollback protection.
        """
        new_template = AssessmentTemplate(**kwargs)
        try:
            self.db.add(new_template)
            self.db.commit()
            self.db.refresh(new_template)
            return new_template
        except IntegrityError as e:
            self.db.rollback()  # 🛡️ Reset session if subject ID or foreign keys do not exist
            raise DatabaseValidationError("Failed to create assessment template. Verify subject ID and constraints.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while creating the assessment template.") from e

    def update(self, template_id: int, **kwargs) -> Optional[AssessmentTemplate]:
        """
        Updates assessment template details safely with transaction protection.
        """
        template = self.get_by_id(template_id)
        if not template:
            return None

        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
            else:
                raise AttributeError(f"AssessmentTemplate model has no attribute '{key}'")

        try:
            self.db.commit()
            self.db.refresh(template)
            return template
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseValidationError("Failed to update assessment template due to database conflicts.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while updating the assessment template.") from e

    def delete(self, template_id: int) -> bool:
        """
        Deletes an assessment template safely.
        """
        template = self.get_by_id(template_id)
        if template:
            try:
                self.db.delete(template)
                self.db.commit()
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseValidationError("Failed to delete assessment template. Ensure associated scores are removed first.") from e
        return False

    def get_by_id(self, template_id: int) -> Optional[AssessmentTemplate]:
        """Fetches an assessment template by ID. Read-only."""
        return self.db.query(AssessmentTemplate).filter(AssessmentTemplate.id == template_id).first()