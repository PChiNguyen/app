from uuid import UUID 
from sqlalchemy import func 
from sqlalchemy.orm import Session
from typing import Optional   
from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore


class StudentScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # 1. THE SYSTEM FUNCTION (Used when a test is announced)
    # ==========================================
    def bulk_create_empty_slots(self, template_id: int, student_ids: list[UUID]):
        """
        Creates blank score slots for an entire classroom. 
        The teacher does NOT call this directly.
        """
        empty_scores = [
            StudentScore(
                student_id=student_id, 
                assessment_template_id=template_id, 
                score=None # Status will automatically default to PENDING
            ) 
            for student_id in student_ids
        ]
        
        self.db.add_all(empty_scores)
        self.db.commit()
        for score in empty_scores:
            self.db.refresh(score)
        
        # we can not refresh because there are multiple objects 
        return empty_scores

    # ==========================================
    # 2. THE TEACHER FUNCTION (Used for grading)
    # ==========================================
    def update_score(self, score_id: UUID, new_score: float):
        db_score = self.db.query(StudentScore).filter(StudentScore.id == score_id).first()
        
        if db_score:
            db_score.score = new_score
            self.db.commit()
            self.db.refresh(db_score)
            
        return db_score
    
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
    