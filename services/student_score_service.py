from repositories.student_score_repo import StudentScoreRepository 
from repositories.assessment_template_repo import AssessmentTemplateRepository 
from repositories.student_repo import StudentRepository 
from repositories.subject_repo import SubjectRepository
from uuid import UUID   
from sqlalchemy.orm import Session
from fastapi import HTTPException


from schemas.student_score_schemas import StudentScoreUpdate, StudentScoreCreate 




class StudentScoreService:
    def __init__(self, db: Session):
        self.score_repo = StudentScoreRepository(db)
        self.template_repo = AssessmentTemplateRepository(db)
        self.student_repo = StudentRepository(db)
        self.subject_repo = SubjectRepository(db)

    def bulk_create_empty_slots(self, template_id: int, student_ids: list[UUID]):
        # 1. BOUNCER: Check if the template exists
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found")
        
        # 2. BOUNCER: Check if the list is empty (don't waste DB time)
        if not student_ids:
            raise HTTPException(status_code=400, detail="Must provide at least one student ID")

        # 3. BOUNCER: The Batch Check! (1 single query for 45 students)
        # We remove duplicates from the list just in case the frontend sent the same ID twice
        unique_student_ids = list(set(student_ids))
        valid_count = self.student_repo.count_by_ids(unique_student_ids)
        
        if valid_count != len(unique_student_ids):
            raise HTTPException(
                status_code=400, 
                detail="One or more student IDs provided do not exist in the system."
            )
        
        # 4. ALL CHECKS PASSED: Now we can safely create the slots!
        return self.score_repo.bulk_create_empty_slots(template_id, unique_student_ids)

        # 4. ALL CHECKS PASSED: Now we can safely build the slots!
        # ... logic to create the scores ...
    def create_score(self, score_in: StudentScoreCreate):
        # 1. BOUNCER: Check if the student exists
        student = self.student_repo.get_by_id(score_in.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        # 2. BOUNCER: Check if the template exists
        template = self.template_repo.get_by_id(score_in.assessment_template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found")
        
        # 3. ALL CHECKS PASSED: Now we can safely create the score!
        return self.score_repo.create_score(score_in)

    def update_score(self, score_id: UUID, score_in: StudentScoreUpdate):
        # 1. BOUNCER: Check if the score slot exists
        db_score = self.score_repo.get_by_id(score_id)
        if not db_score:
            raise HTTPException(status_code=404, detail="Score slot not found")
        updates= score_in.model_dump(exclude_unset=True) 
        
        ## schemas should have already validated that the new_score is a valid float, so we can skip that check here
        
        # 3. ALL CHECKS PASSED: Now we can safely update the score!
        return self.score_repo.update_score(score_id, **updates)
    
    def get_scores_by_student_id(self, student_id: UUID):
        # 1. BOUNCER: Check if the student exists
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # 2. ALL CHECKS PASSED: Now we can safely retrieve the scores!
        return self.score_repo.get_by_student_id(student_id)
    def get_scores_by_template_id(self, template_id: int):
        # 1. BOUNCER: Check if the template exists
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found")
        
        # 2. ALL CHECKS PASSED: Now we can safely retrieve the scores!
        return self.score_repo.get_by_template_id(template_id)
    def get_scores_by_student_id_and_subject_id(self, student_id: UUID, subject_id: int):
        # 1. BOUNCER: Check if the student exists
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        # 2. BOUNCER: Check if the subject exists
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        # 2. ALL CHECKS PASSED: Now we can safely retrieve the scores!
        return self.score_repo.get_by_student_id_and_subject_id(student_id, subject_id)
        

    def delete_score(self, score_id: UUID):
        """
        Validates existence before deleting. 
        Raises 404 so the API router doesn't have to think.
        """
        # 1. Bouncer Check: Does it exist?
        score = self.score_repo.get_by_id(score_id)
        if not score:
            raise HTTPException(status_code=404, detail="Student score not found")
            
        # 2. Execution
        return self.score_repo.delete(score_id)

        

        
    
