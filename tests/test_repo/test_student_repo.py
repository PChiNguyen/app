
import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

import pytest 
from repositories.student_repo import StudentRepository
from repositories.classroom_repo import ClassroomRepository 
from repositories.user_repo import UserRepository 
import uuid
from sqlalchemy.exc import IntegrityError    
@pytest.fixture
def teacher(db_session):
    user_repo = UserRepository(db_session)
    return user_repo.create(
        username=f"teacher_{uuid.uuid4().hex[:6]}", 
        email=f"teacher_{uuid.uuid4().hex[:6]}@school.com",
        password="secure_hash",
        role="teacher"
    )

# 2. THE COMPOSITION: Create a Classroom using the Teacher
@pytest.fixture
def classroom(db_session, teacher):
    class_repo = ClassroomRepository(db_session)
    # We inject 'teacher' above and use teacher.id here
    return class_repo.create(name="Mathematics", teacher_id=teacher.id)
@pytest.fixture
def student_repo(db_session):
    return StudentRepository(db_session)

def test_create_student(student_repo,classroom):
    student_id = student_repo.create(name="Student One", classroom_id=classroom.id) 
    assert student_id is not None
def create_with_non_existent_classroom(student_repo):
    with pytest.raises(IntegrityError):
        student_repo.create(name="Student One", classroom_id=uuid.uuid4())

def test_get_by_id(student_repo,classroom):
    student= student_repo.create(name="Student Two", classroom_id=classroom.id)
    student = student_repo.get_by_id(student.id)
    assert student is not None
    assert student.name == "Student Two"

def test_get_by_classroom_id(student_repo,classroom):
    student1_id = student_repo.create(name="Student Three", classroom_id=classroom.id)
    student2_id = student_repo.create(name="Student Four", classroom_id=classroom.id)
    students = student_repo.get_by_classroom_id(classroom.id)
    assert len(students) == 2
    assert students[0].name == "Student Three"
    assert students[1].name == "Student Four"
def test_delete_student(student_repo,classroom):
    student = student_repo.create(name="Student Five", classroom_id=classroom.id)
    result= student_repo.delete(student.id)
    assert result is True             
     
    