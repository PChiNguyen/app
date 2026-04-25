
import uuid

import pytest
from sqlalchemy import Connection, Engine, create_engine, event 
from sqlalchemy.orm import sessionmaker, Session 
from fastapi.testclient import TestClient
from api.deps import get_current_user
from db.models.user import User, UserRole
from db.session import get_db
from main import app
from core.config import settings


from db.base import Base
from repositories.classroom_repo import ClassroomRepository
from repositories.grade_repo import GradeRepository
from repositories.student_repo import StudentRepository 


MOCK_TEACHER_ID = uuid.uuid4()


@pytest.fixture
def mock_teacher(db_session):
    """Global fixture to create a teacher. Only runs when requested."""
    teacher = User(
        id=MOCK_TEACHER_ID,
        username="teacher_nguyen", 
        email="nguyen@abc.com",
        password_hash="abc",
        role=UserRole.TEACHER
    )
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher

@pytest.fixture
def mock_classroom(db_session, mock_teacher):
    """Global fixture to create a classroom. Notice no 'autouse=True'."""
    repo = ClassroomRepository(db_session)
    classroom = repo.create(name="Science", teacher_id=mock_teacher.id)
    return classroom

@pytest.fixture
def mock_student(db_session, mock_classroom):
    repo = StudentRepository(db_session)
    student = repo.create(name="Thảo Nguyên", classroom_id = mock_classroom.id)
    return student
@pytest.fixture
def mock_student_grades(db_session, mock_student):
    # Create some mock grades for the student
    grade_repo= GradeRepository(db_session)
    grade1 = grade_repo.create(subject="Math", score=8.5, student_id=mock_student.id)
    grade2 = grade_repo.create(subject="Science", score=9.0, student_id=mock_student.id)


@pytest.fixture(autouse=True)
def setup_dependency_override(mock_teacher):
    """
    autouse=True means this runs automatically for every test in this file.
    It takes the mock_teacher we just saved, and hands it directly to FastAPI.
    """
    def override():
        return mock_teacher

    app.dependency_overrides[get_current_user] = override
    yield # Let the test run
    app.dependency_overrides.clear() # Clean up afterwards

@pytest.fixture
def client(db_session):
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    ## this tells fastapi to run the _get_test_db function instead of the original get_db function whenever a test needs a database session.
    
    # Using 'with' ensures the startup/shutdown events of FastAPI run
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest.fixture(scope='session')    
def engine():
    _engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 1. Register the listener (DO NOT put yield here)
    @event.listens_for(_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # 2. Import models so Base can see them
    from db.models.user import User
    from db.models.classroom import Classroom
    from db.models.student import Student
    from db.models.grade import Grade

    # 3. Build the structure (This is outside the listener!)
    Base.metadata.create_all(bind=_engine)
    
    # 4. Give the engine to the tests
    yield _engine
    
    # 5. Cleanup
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(scope='function')
def db_session(engine:Engine):
    connection: Connection= engine.connect() 
    transaction= connection.begin()
    session_factory= sessionmaker(bind=connection)

    session:Session= session_factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()   




