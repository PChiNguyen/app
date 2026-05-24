from sqlalchemy.orm import Session
from typing import Optional
from db.models.subject import Subject

class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Subject]:
        return self.db.query(Subject).all()

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_by_name(self, name: str) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.name == name).first()