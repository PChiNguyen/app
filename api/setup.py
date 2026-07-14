from api.deps import get_db, get_current_admin
from db.models.user import User
from repositories.subject_repo import SubjectRepository
from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from db.models.user import User, UserRole 

router= APIRouter()  

@router.post("/system/init-subjects", tags=["System Setup"])
def initialize_school_subjects(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_admin) <-- Bye bye bouncer!
):
    subject_repo = SubjectRepository(db)
    subjects_to_initialize = ["Mathematics", "Science", "History", "Literature", "Art", "Physical Education", "Computer Science"]
    for subject_name in subjects_to_initialize:
        existing_subject = subject_repo.get_by_name(subject_name)
        if not existing_subject:
            subject_repo.create(subject_name)
    return {"message": "Semester subjects initialized successfully."} 




