from repositories.subject_repo import SubjectRepository
from sqlalchemy.orm import Session
from fastapi import HTTPException


class SubjectService:
    def __init__(self, db: Session):
        self.subject_repo = SubjectRepository(db)
    
    def create_subject(self, name: str): 
        existing_subject = self.subject_repo.get_by_name(name)
        if existing_subject:
            raise HTTPException(status_code=400, detail="Subject already exists")
        return self.subject_repo.create(name)
    def get_all_subjects(self):
        all_subjects = self.subject_repo.get_all()
        if not all_subjects:
            raise HTTPException(status_code=404, detail="No subjects found")
        return all_subjects
    def get_subject_by_id(self, subject_id: int):
        subject = self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject
    
    def get_subject_by_name(self, name: str):
        subject = self.subject_repo.get_by_name(name)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject

        