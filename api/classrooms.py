from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from api.deps import get_db, get_current_user, get_current_teacher
from schemas.classroom import ClassroomRead, ClassroomCreate, ClassroomUpdate, StudentRankingRead 
from services.classroom_service import ClassroomService 
from db.models.user import User

router= APIRouter()


@router.post('/', response_model= ClassroomRead, status_code= status.HTTP_201_CREATED)
def create_classroom(*,
                     db: Session = Depends(get_db),
                     current_user= Depends(get_current_teacher),
                     classroom_in: ClassroomCreate):
## the '*' ensures that all parameters after it must be passed as keyword arguments, not positional arguments. This is a common practice in FastAPI to improve code readability and prevent errors when calling the function.
    service: ClassroomService = ClassroomService(db)    

    classroom= service.create_classroom(classroom_in.name, current_user.id)

    return classroom 



#####
@router.get('/', response_model= List[ClassroomRead])
def read_classrooms(*,skip: int = 0, limit: int = 100,
                    db: Session = Depends(get_db),
                    current_user= Depends(get_current_teacher)):
    service: ClassroomService = ClassroomService(db) 
    classrooms= service.list_all_classrooms(skip=skip, limit=limit)
    return classrooms


from services.classroom_service import ClassroomService  # 1. Import your service layer!

@router.get('/teacher/{teacher_id}', response_model=List[ClassroomRead])
def read_classrooms_by_teacher(*, 
                               db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_teacher)):
    """
    Fetches all classrooms assigned to a specific teacher ID.
    Delegates validation and lookup to the ClassroomService layer.
    """
    # 2. Instantiate the service brain instead of bypassing it
    service = ClassroomService(db)
    
    # 3. Call the service method (It automatically raises a 404 if the teacher doesn't exist!)
    classrooms = service.list_classrooms_by_teacher_id(current_user.id)
    
    return classrooms

@router.get('/{classroom_id}', response_model= ClassroomRead)
def read_classroom(*, classroom_id: UUID,
                   db: Session = Depends(get_db),
                   current_user= Depends(get_current_teacher)):
    service: ClassroomService = ClassroomService(db) 
    classroom= service.get_classroom(classroom_id)
    if not classroom:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= "Classroom not found"
        )
    return classroom



@router.put('/{classroom_id}', response_model=ClassroomRead)
def update_classroom(*, 
                     classroom_id: UUID,
                     db: Session = Depends(get_db),
                     current_user= Depends(get_current_teacher),
                     classroom_in: ClassroomUpdate):
    service = ClassroomService(db) 
    
    # 🛠️ Pass the Pydantic box cleanly. No logic, no dictionary unpacking here!
    return service.update_classroom(classroom_id, classroom_in)

@router.delete('/{classroom_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_classroom(*, classroom_id: UUID,
                     db: Session = Depends(get_db),
                     current_user= Depends(get_current_teacher)):
    service: ClassroomService = ClassroomService(db) 
    delete_success= service.delete_classroom(classroom_id)
    return None
    







    

