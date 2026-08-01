from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.cache_decorator import invalidate_cache
from core.lock_decorator import distributed_lock
from repositories.assessment_template_repo import AssessmentTemplateRepository
from repositories.student_repo import StudentRepository
from repositories.student_score_repo import StudentScoreRepository
from repositories.subject_repo import SubjectRepository
from schemas.student_score_schemas import StudentScoreCreate, StudentScoreUpdate


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

        # 2. BOUNCER: Check if the list is empty
        if not student_ids:
            raise HTTPException(
                status_code=400, detail="Must provide at least one student ID"
            )

        # 3. BOUNCER: Batch Check student existence
        unique_student_ids = list(set(student_ids))
        valid_count = self.student_repo.count_by_ids(unique_student_ids)

        if valid_count != len(unique_student_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more student IDs provided do not exist in the system.",
            )

        # 4. ALL CHECKS PASSED: Safely create empty score slots
        return self.score_repo.bulk_create_empty_slots(template_id, unique_student_ids)

    # 🟢 ADDED: Automatically clear GPA cache when a new score is created
    @invalidate_cache(prefixes=["gpa:"])
    def create_score(self, score_in: StudentScoreCreate):
        # 1. BOUNCER: Check if the student exists
        student = self.student_repo.get_by_id(score_in.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # 2. BOUNCER: Check if the template exists
        template = self.template_repo.get_by_id(score_in.assessment_template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found")

        # 3. TRANSFORM: Convert Pydantic model to dictionary
        score_data = score_in.model_dump()

        # 4. ALL CHECKS PASSED: Create score and purge old GPA cache
        return self.score_repo.create_score(**score_data)

    @distributed_lock(
        lock_key_pattern="lock:score:{score_id}", timeout=5, blocking_timeout=2.0
    )
    @invalidate_cache(prefixes=["gpa:"])
    def update_score(self, score_id: UUID, score_in: StudentScoreUpdate):
        """
        Updates student score in DB and automatically triggers Redis cache
        invalidation for all GPA/Average keys starting with 'gpa:'.
        """
        # 1. BOUNCER: Check if the score slot exists
        db_score = self.score_repo.get_by_id(score_id)
        if not db_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Score slot not found"
            )

        # 2. Extract only fields sent in request body
        updates = score_in.model_dump(exclude_unset=True)

        # 3. ALL CHECKS PASSED: Update in DB
        return self.score_repo.update_score(score_id, **updates)

    # 🟢 ADDED: Redis Lock & Cache Invalidation for Delete operations
    @distributed_lock(
        lock_key_pattern="lock:score:{score_id}", timeout=5, blocking_timeout=2.0
    )
    @invalidate_cache(prefixes=["gpa:"])
    def delete_score(self, score_id: UUID):
        """
        Validates existence, acquires lock, deletes score, and automatically
        invalidates all stale GPA caches starting with 'gpa:'.
        """
        # 1. BOUNCER: Check if score exists
        score = self.score_repo.get_by_id(score_id)
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student score not found"
            )

        # 2. EXECUTION: Delete from DB & fire @invalidate_cache automatically
        return self.score_repo.delete(score_id)

    def get_scores_by_student_id(self, student_id: UUID):
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return self.score_repo.get_by_student_id(student_id)

    def get_scores_by_template_id(self, template_id: int):
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Assessment template not found")
        return self.score_repo.get_by_template_id(template_id)

    def get_scores_by_student_id_and_subject_id(
        self, student_id: UUID, subject_id: int
    ):
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return self.score_repo.get_by_student_id_and_subject_id(
            student_id, subject_id
        )