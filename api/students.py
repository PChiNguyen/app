from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_teacher
from schemas.student import StudentRead, StudentCreate, StudentUpdate
from services.student_service import StudentService # ✅ The real brain imported!

router = APIRouter() 

@router.post('/', response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(*, 
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_teacher),
                   student_in: StudentCreate):
    # Pass the Pydantic box straight down. No unpacking here!
    return StudentService(db).create_student(student_in.name, student_in.classroom_id)

@router.get('/', response_model=List[StudentRead])
def read_students(*, 
                  skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db),
                  current_user = Depends(get_current_teacher)):
    return StudentService(db).get_multi_students(skip=skip, limit=limit) 

@router.get('/{student_id}', response_model=StudentRead)
def read_student(*, 
                 student_id: UUID,
                 db: Session = Depends(get_db),
                 current_user = Depends(get_current_teacher)):
    # The service raises the 404 error if missing. We just return!
    return StudentService(db).get_student_by_id(student_id)

@router.put('/{student_id}', response_model=StudentRead)
def update_student(*, 
                   student_id: UUID,
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_teacher),
                   student_in: StudentUpdate):
    # No .model_dump() needed! The service handles the exclude_unset logic.
    return StudentService(db).update_student(student_id, student_in)

@router.delete('/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student(*, 
                   student_id: UUID,
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_teacher)):
    # The service runs all safety checks before deleting.
    StudentService(db).delete_student(student_id)
    return None