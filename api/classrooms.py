from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models.grade import Grade
from services.gpa import calc_gpa 
from services.ranking import rank_by_gpa 
from repositories.student_repo import StudentRepository
from repositories.grade_repo import GradeRepository

from api.deps import get_db, get_current_user, get_current_teacher
from schemas.classroom import ClassroomRead, ClassroomCreate, ClassroomUpdate, StudentRankingRead 
from repositories.classroom_repo import ClassroomRepository, LeaderboardRow 

router= APIRouter()


@router.post('/', response_model= ClassroomRead, status_code= status.HTTP_201_CREATED)
def create_classroom(*,
                     db: Session = Depends(get_db),
                     current_user= Depends(get_current_teacher),
                     classroom_in: ClassroomCreate):
## the '*' ensures that all parameters after it must be passed as keyword arguments, not positional arguments. This is a common practice in FastAPI to improve code readability and prevent errors when calling the function.
    repo= ClassroomRepository(db)      

    classroom= repo.create(classroom_in.name, current_user.id)

    return classroom 

@router.get('/', response_model= List[ClassroomRead])
def read_classrooms(*,skip: int = 0, limit: int = 100,
                    db: Session = Depends(get_db),
                    current_user= Depends(get_current_teacher)):
    repo= ClassroomRepository(db)
    classrooms= repo.get_multi(skip=skip, limit=limit)
    return classrooms

@router.get('/{classroom_id}', response_model= ClassroomRead)
def read_classroom(*, classroom_id: UUID,
                   db: Session = Depends(get_db),
                   current_user= Depends(get_current_teacher)):
    repo= ClassroomRepository(db)
    classroom= repo.get_by_id(classroom_id)
    if not classroom:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Classroom not found"
        )
    return classroom

@router.put('/{classroom_id}', response_model= ClassroomRead)
def update_classroom(*, classroom_id: UUID,
                     db: Session = Depends(get_db),
                     current_user= Depends(get_current_teacher),
                     classroom_in: ClassroomUpdate):
    repo= ClassroomRepository(db)
    update_data = classroom_in.model_dump(exclude_unset=True)
    ## this changes the classroom_in object (which is a pydantic model) into a python dictionary, but only includes the fields that were actually provided in the request (exclude_unset=True). This allows for partial updates, where the client can send only the fields they want to update instead of having to send the entire object.
    classroom= repo.get_by_id(classroom_id)
    if not classroom:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Classroom not found"
        )
    updated_classroom= repo.update(classroom_id = classroom_id, **update_data)
    if not updated_classroom:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Failed to update classroom"
        )
    return updated_classroom  

@router.delete('/{classroom_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_classroom(*, classroom_id: UUID,
                     db: Session = Depends(get_db),
                     current_user= Depends(get_current_teacher)):
    repo= ClassroomRepository(db)
    delete_success= repo.delete(classroom_id)
    if not delete_success:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Classroom not found"
        )
    return None
@router.get('/{classroom_id}/ranking')
def get_class_ranking(*, classroom_id: UUID,
                      db: Session = Depends(get_db),
                      current_user= Depends(get_current_teacher)):
    repo= ClassroomRepository(db)
    ranking= repo.get_class_ranking(classroom_id)
    if ranking is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Classroom not found"
        )
    formatted_ranking = [
        {
            "student_id": row.student_id,
            "name": row.student_name,  # Mapping "student_name" to "name"
            "gpa": round(row.gpa, 1) if row.gpa else 0.0,
            "class_rank": row.class_rank     # Mapping "rank" to "class_rank"
        }
        for row in ranking
    ]
    
    return formatted_ranking



    

