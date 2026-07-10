from services.student_service import StudentService
from db.models.student import Student
from db.models.classroom import Classroom
import pytest
from fastapi import HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session 
from tests.conftest import db_session
from schemas.student import StudentUpdate  

def student_service(db_session: Session):
    return StudentService(db_session)
## test create student
def test_create_student_invalid_classroom(db_session: Session):
    service = StudentService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.create_student("Test Student", uuid4())
    assert exc_info.value.status_code == 404

## test get student by id
def test_get_student_by_id_not_found(db_session):
    service = StudentService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_student_by_id(uuid4())
    assert exc_info.value.status_code == 404


## test update student
def test_update_student_not_found(db_session):
    service = StudentService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.update_student(uuid4(), {"name": "New Name"})
    assert exc_info.value.status_code == 404



## test delete student
def test_delete_student_not_found(db_session):
    service = StudentService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.delete_student(uuid4())
    assert exc_info.value.status_code == 404

def test_delete_student_with_scores(db_session, mock_student: Student, mock_student_score_semester1, mock_student_score_semester2):
    service = StudentService(db_session)
    # Assuming mock_student has associated scores in the database
    with pytest.raises(HTTPException) as exc_info:
        service.delete_student(mock_student.id)
    assert exc_info.value.status_code == 400 

## test list students by classroom
def test_list_students_by_classroom_not_found(db_session):
    service = StudentService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.list_students_by_classroom(uuid4())
    assert exc_info.value.status_code == 404 


def test_create_student_success(db_session, mock_classroom: Classroom):
    service = student_service(db_session)
    new_student = service.create_student(name="Lê Lợi", classroom_id=mock_classroom.id)
    assert new_student is not None
    assert new_student.name == "Lê Lợi"
    assert new_student.classroom_id == mock_classroom.id

def test_get_student_by_id_success(db_session, mock_student: Student):
    service = student_service(db_session)
    student = service.get_student_by_id(mock_student.id)
    assert student.name == "Thảo Nguyên"

def test_update_student_success(db_session, mock_student: Student):
    service = student_service(db_session)
    # Updating just the name
    update = StudentUpdate(name="Nguyễn Văn A")
    updated = service.update_student(mock_student.id, update)
    assert updated.name == "Nguyễn Văn A"

def test_delete_student_success(db_session, mock_classroom: Classroom):
    service = student_service(db_session)
    # 1. Create a fresh student with no scores
    temp_student = service.create_student(name="Temporary Student", classroom_id=mock_classroom.id)
    
    # 2. Delete them successfully!
    result = service.delete_student(temp_student.id)
    assert result is True

def test_list_students_by_classroom_success(db_session, mock_classroom: Classroom, mock_student: Student):
    service = student_service(db_session)
    students = service.list_students_by_classroom(mock_classroom.id)
    assert isinstance(students, list)
    assert len(students) >= 1
    assert students[0].id == mock_student.id

def test_get_multi_students_success(db_session, mock_student: Student):
    service = student_service(db_session)
    students = service.get_multi_students(skip=0, limit=10)
    assert isinstance(students, list)
    assert len(students) >= 1