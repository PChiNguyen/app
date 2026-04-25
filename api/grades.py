from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from db.models import grade
from schemas.grade import GradeRead, GradeCreate, GradeUpdate
from repositories.grade_repo import GradeRepository

router = APIRouter() 


@router.post('/', response_model= GradeRead, status_code= status.HTTP_201_CREATED)
def create_grade(*, db: Session = Depends(get_db),
    current_user= Depends(get_current_user),
    grade_in: GradeCreate):    
    repo= GradeRepository(db)    
    grade= repo.create(subject= grade_in.subject, score= grade_in.score, student_id= grade_in.student_id, coefficient= grade_in.coefficient)
    return grade
@router.get('/student/{student_id}', response_model= List[GradeRead])
def read_grades_by_student(*, student_id: UUID,
    db: Session = Depends(get_db),
    current_user= Depends(get_current_user)):
    repo= GradeRepository(db)
    grades= repo.get_by_student_id(student_id)
    return grades

@router.get('/{grade_id}', response_model= GradeRead)
def read_grade(*, grade_id: UUID,
    db: Session = Depends(get_db),
    current_user= Depends(get_current_user)):    
    repo= GradeRepository(db)    
    grade= repo.get_by_id(grade_id)
    if not grade:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Grade not found"
        )
    return grade
@router.put('/{grade_id}', response_model= GradeRead)
def update_grade(*, grade_id: UUID,
    db: Session = Depends(get_db),
    current_user= Depends(get_current_user),
    grade_in: GradeUpdate):
    repo= GradeRepository(db)
    update_data = grade_in.model_dump(exclude_unset=True)
    grade= repo.get_by_id(grade_id)
    if not grade:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Grade not found"
        )
    updated_grade= repo.update(grade_id = grade_id, **update_data)
    return updated_grade

@router.get('/', response_model= List[GradeRead])
def read_grades_by_subject(*, db: Session = Depends(get_db),
    current_user= Depends(get_current_user),
    subject: str, skip: int = 0, limit: int = 100):
    repo= GradeRepository(db)
    grades= repo.get_multi_by_subject(subject, skip=skip, limit=limit)    
    if not grades:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Grades not found"
        )
    return grades

@router.delete('/{grade_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_grade(*, grade_id: UUID,
    db: Session = Depends(get_db),
    current_user= Depends(get_current_user)):
    repo= GradeRepository(db)
    success= repo.delete(grade_id)
    if not success:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Grade not found"
        )    
    return None             
