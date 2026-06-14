from services.classroom_service import ClassroomService
from db.models.classroom import Classroom
from db.models.student import Student 
from db.models.user import User
from db.models.subject import Subject 
from sqlalchemy.orm import Session
from fastapi import HTTPException
import pytest
from uuid import uuid4 

def test_create_classroom_with_invalid_teacher_id(db_session: Session):
    service = ClassroomService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.create_classroom("Math", uuid4())
    assert exc_info.value.status_code == 404 

def test_get_classroom_with_invalid_classroom_id(db_session: Session):
    service = ClassroomService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_classroom(uuid4())
    assert exc_info.value.status_code == 404 

def test_update_classroom_with_invalid_classroom_id(db_session: Session):
    service = ClassroomService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.update_classroom(uuid4(), {"name": "New Name"})
    assert exc_info.value.status_code == 404 

def test_delelte_classroom_with_students_in(db_session: Session, mock_classroom: Classroom, mock_student: Student):
    service = ClassroomService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.delete_classroom(mock_classroom.id)
    assert exc_info.value.status_code == 400 





def test_create_classroom_success(db_session, mock_teacher: User):
    service = ClassroomService(db_session)
    # Happy path: We have a valid teacher ID
    new_class = service.create_classroom(name="math", teacher_id=mock_teacher.id)
    assert new_class is not None
    assert new_class.name == "math"
    assert new_class.teacher_id == mock_teacher.id

def test_get_classroom_success(db_session, mock_classroom: Classroom):
    service = ClassroomService(db_session)
    fetched_class = service.get_classroom(mock_classroom.id)
    assert fetched_class.name == "Science"

def test_update_classroom_success(db_session, mock_classroom: Classroom, mock_subject: Subject):
    service = ClassroomService(db_session)
    # Updating the name while leaving the teacher_id intact
    updated_class: Classroom = service.update_classroom(mock_classroom.id,{"name": "Science"} )
    assert updated_class.name == "Science"

def test_list_classrooms_by_teacher_id_success(db_session, mock_classroom: Classroom, mock_teacher: User):
    service = ClassroomService(db_session)
    # Verify the teacher can see their assigned rooms
    classrooms = service.list_classrooms_by_teacher_id(mock_teacher.id)
    assert isinstance(classrooms, list)
    assert len(classrooms) >= 1
    assert classrooms[0].id == mock_classroom.id

def test_list_all_classrooms_success(db_session, mock_classroom: Classroom):
    service = ClassroomService(db_session)
    # Verify pagination works correctly
    classrooms = service.list_all_classrooms(skip=0, limit=10)
    assert isinstance(classrooms, list)
    assert len(classrooms) >= 1
