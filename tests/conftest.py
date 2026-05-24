
import uuid

import pytest
from sqlalchemy import Connection, Engine, create_engine, event 
from sqlalchemy.orm import sessionmaker, Session 
from fastapi.testclient import TestClient
from api.deps import get_current_user
from db.models.assessment_template import AssessmentTemplate
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.subject import Subject
from db.models.user import User, UserRole
from db.session import get_db
from main import app
from core.config import settings


from db.base import Base
from repositories.classroom_repo import ClassroomRepository
from repositories.student_repo import StudentRepository 


MOCK_TEACHER_ID = uuid.uuid4()


@pytest.fixture
def mock_teacher(db_session: Session):
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
def mock_classroom(db_session: Session, mock_teacher: User):
    """Global fixture to create a classroom. Notice no 'autouse=True'."""
    repo = ClassroomRepository(db_session)
    classroom = repo.create(name="Science", teacher_id=mock_teacher.id)
    return classroom

@pytest.fixture
def mock_student(db_session: Session, mock_classroom: Classroom):
    repo = StudentRepository(db_session)
    student = repo.create(name="Thảo Nguyên", classroom_id = mock_classroom.id)
    return student
@pytest.fixture
def mock_subject(db_session: Session):
    from db.models.subject import Subject
    subject = Subject(name="Math")
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)
    return subject
@pytest.fixture
def mock_assessment_template(db_session: Session, mock_subject: Subject):
    from db.models.assessment_template import AssessmentTemplate
    template = AssessmentTemplate(name="Math Test", type="test", semester=1, subject_id=mock_subject.id)
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template
@pytest.fixture
def mock_student_score(db_session: Session, mock_student: Student, mock_assessment_template: AssessmentTemplate     ):
    from db.models.student_score import StudentScore
    score = StudentScore(student_id=mock_student.id, assessment_template_id=mock_assessment_template.id, score=9.5)
    db_session.add(score)
    db_session.commit()
    db_session.refresh(score)
    return score



@pytest.fixture(autouse=True)
def setup_dependency_override(mock_teacher: User):
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
    from db.models.subject import  Subject
    from db.models.assessment_template import  AssessmentTemplate
    from db.models.student_score import StudentScore 

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




