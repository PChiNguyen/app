from sqlalchemy.orm import Session
from typing import Optional
from db.models.subject import Subject, SubName

class SubjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str) -> Subject:
        new_subject = Subject(name=name)
        self.db.add(new_subject)
        self.db.commit()
        self.db.refresh(new_subject)
        return new_subject

    def get_all(self) -> list[Subject]:
        return self.db.query(Subject).all()

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_by_name(self, name: str) -> Optional[Subject]:
        return self.db.query(Subject).filter(Subject.name == name).first()
    


    