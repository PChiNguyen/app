from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_student, get_current_teacher, get_db, get_current_user
from schemas.student import StudentRead, StudentCreate, StudentUpdate
from repositories.student_repo import StudentRepository
from repositories.classroom_repo import ClassroomRepository 


router = APIRouter() 


@router.post('/', response_model = StudentRead, status_code= status.HTTP_201_CREATED)
def create_student(*, db: Session = Depends(get_db),
                   current_user= Depends(get_current_teacher),
                   student_in: StudentCreate):
    student_repo= StudentRepository(db)
    classroom_repo= ClassroomRepository(db) 
    classroom= classroom_repo.get_by_id(student_in.classroom_id)
    if not classroom:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Classroom not found"
        )
    student= student_repo.create(name= student_in.name, classroom_id= student_in.classroom_id)
    return student
@router.get('/', response_model= List[StudentRead])
def read_students(*, skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db),
                  current_user= Depends(get_current_teacher)):
    student_repo= StudentRepository(db)
    students= student_repo.get_multi(skip=skip, limit=limit)
    return students 
@router.get('/{student_id}', response_model= StudentRead)
def read_student(*, student_id: UUID,
                 db: Session = Depends(get_db),
                 current_user= Depends(get_current_teacher)):
    repo= StudentRepository(db)
    student= repo.get_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Student not found"
        )
    return student
@router.put('/{student_id}', response_model= StudentRead)
def update_student(*, student_id: UUID,
                   db: Session = Depends(get_db),
                   current_user= Depends(get_current_teacher),
                   student_in: StudentUpdate):
    repo= StudentRepository(db)
    update_data = student_in.model_dump(exclude_unset=True)
    ## this exclude_unset=True allows for partial updates, where the client can send only the fields they want to update instead of having to send the entire object.
    ## we use this to avoid problems like accidentally setting a field to null just because the client forgot to include it in the update request.
    student= repo.get_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Student not found"
        )
    updated_student= repo.update(student_id = student_id, **update_data)
    return updated_student

@router.delete('/{student_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_student(*, student_id: UUID,
                   db: Session = Depends(get_db),
                   current_user= Depends(get_current_teacher)):
    repo= StudentRepository(db)
    delete_success= repo.delete(student_id)
    if not delete_success:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Student not found"
        )
    return None

# 2. THE STUDENT ENDPOINT
@router.get('/me/report-card')
def get_report_card(*, db: Session = Depends(get_db),
                    current_user= Depends(get_current_student)):
    repo= StudentRepository(db)
    report_card = repo.get_student_rank_and_gpa(current_user.id)
    if not report_card:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Report card not found"
        )
    return {
        "student_id": report_card.student_id,
        "name": report_card.student_name,
        "gpa": round(report_card.gpa, 1) if report_card.gpa else 0.0,
        "class_rank": report_card.rank
    }
@router.get('/{student_id}/report-card')
def get_student_report_card_for_teacher(*, student_id: UUID,
                                db: Session = Depends(get_db),
                                current_user= Depends(get_current_teacher)):
    repo= StudentRepository(db)
    report_card = repo.get_student_rank_and_gpa(student_id)
    if not report_card:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Report card not found"
        )
    return {
        "student_id": report_card.student_id,
        "name": report_card.student_name,
        "gpa": round(report_card.gpa, 1) if report_card.gpa else 0.0,
        "class_rank": report_card.rank
    }



