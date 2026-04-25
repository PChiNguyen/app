from sqlalchemy.exc import IntegrityError 
import pytest
from repositories.user_repo import UserRepository
from db.models.user import User, UserRole
import traceback 



def test_create_user(db_session):
    repo=UserRepository(db_session)
    user=repo.create(username="testuser",email="test@abc.com",password="abc",role="student")
    assert user.id is not None
    assert user.username=="testuser"
    assert user.email=="test@abc.com".strip()
    assert user.role==UserRole.STUDENT




def test_get_user_by_id(db_session):
    repo= UserRepository(db_session)
    user= repo.create(username="testuser2",email="test2@abc.com",password="abc",role="student")
    found_user= repo.get_by_id(user.id)
    assert found_user is not None



def test_get_user_by_email(db_session):
    repo= UserRepository(db_session)
    user= repo.create(username="testuser3",email="test3@abc.com",password="abc",role="student")
    found_user= repo.get_by_email(user.email)
    assert found_user is not None





    
def test_exists_by_email(db_session):
    repo= UserRepository(db_session)
    email="test4@abc.com"
    assert repo.exists_by_email(email) is False
    repo.create(username="testuser4",email=email,password="abc",role="student")
    assert repo.exists_by_email(email)




def test_delete_user(db_session):
    repo= UserRepository(db_session)
    user= repo.create(username="testuser5",email="test5@abc.com",password="abc",role="student")
    repo.delete(user.id)
    assert repo.get_by_id(user.id) is None


## update 
def test_update_user(db_session):
    repo= UserRepository(db_session)
    user= repo.create(username="testuser6",email="test6@abc.com",password="abc",role="student")
    repo.update(user.id,role="teacher")
    assert repo.get_by_id(user.id).role == UserRole.TEACHER

def test_update_with_invalid_key(db_session):
    repo= UserRepository(db_session)
    user= repo.create(username="testuser6",email="test6@abc.com",password="abc",role="student")
    with pytest.raises(Exception):
        repo.update(user.id,invalid_key='hehe')

    

def test_create_user_with_duplicate_email(db_session):
    repo= UserRepository(db_session)
    email="test7@abc.com"   
    repo.create(username="testuser7",email=email,password="abc",role="student")
    with pytest.raises((IntegrityError, ValueError)) as excinfo:
        repo.create(username="testuser8",email=email,password="abc",role="student")

    # Now you can inspect it
    print(f"The actual error was: {excinfo.type}")
        




   
