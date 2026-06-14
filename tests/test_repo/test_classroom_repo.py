import pytest 
import uuid 
from repositories.classroom_repo import ClassroomRepository
from repositories.user_repo import UserRepository   
from db.models.user import User 
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text 
from sqlalchemy.orm import Session 




@pytest.fixture
def classroom_repo(db_session: Session):
    return ClassroomRepository(db_session)





def test_create_classroom(classroom_repo: ClassroomRepository, mock_teacher: User):


    classroom= classroom_repo.create(name="Math", teacher_id=mock_teacher.id)
    assert classroom.id is not None
    assert classroom.name=="Math"
    assert classroom.teacher_id==mock_teacher.id
def create_classroom_with_nonexistent_teacher(classroom_repo: ClassroomRepository):
    with pytest.raises(IntegrityError):
        classroom_repo.create(name="Math",teacher_id=uuid.uuid4())
   

def test_get_classroom_by_id(classroom_repo: ClassroomRepository, mock_teacher: User):

    classroom= classroom_repo.create(name="Science", teacher_id=mock_teacher.id)
    found_classroom= classroom_repo.get_by_id(classroom.id)
    assert found_classroom is not None
    assert found_classroom.name=="Science"
    assert found_classroom.teacher_id==mock_teacher.id       
def test_get_classrooms_by_teacher_id(classroom_repo: ClassroomRepository, mock_teacher: User):
   
    
    classroom1= classroom_repo.create(name="History", teacher_id=mock_teacher.id)
    classroom2= classroom_repo.create(name="Geography", teacher_id=mock_teacher.id)
    classrooms= classroom_repo.get_by_teacher_id(mock_teacher.id)
    assert len(classrooms)==2
    assert classrooms[0].name=="History"
    assert classrooms[1].name=="Geography"      

def test_delete_classroom(classroom_repo: ClassroomRepository, mock_teacher: User):

    classroom= classroom_repo.create(name="Art", teacher_id=mock_teacher.id)
    result= classroom_repo.delete(classroom.id)
    assert result is True
    assert classroom_repo.get_by_id(classroom.id) is None              
def test_create_classroom_with_nonexistent_teacher(db_session: Session):
    repo= ClassroomRepository(db_session)
    sql=text("INSERT INTO classrooms (id, name, teacher_id) VALUES (:id, :name, :teacher_id)")
    params={
        'id': str(uuid.uuid4()),
        'name': "Music",
        'teacher_id': str(uuid.uuid4())    }
    with pytest.raises(IntegrityError):
        db_session.execute(sql, params)
        db_session.commit()
    

### thêm vào test của hacker, để chỗ user repo test luôn không quên á 



