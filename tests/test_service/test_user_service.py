from services.user_service import UserService 
from db.models.user import User 
import pytest 
from fastapi import HTTPException 
import uuid
from sqlalchemy.orm import Session

## test create
def test_create_user_duplicate_email(db_session: Session,mock_teacher: User):
    service = UserService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.create_user("another_teacher", mock_teacher.email, "abc", "teacher")
    assert exc_info.value.status_code == 400

## test get by id
def test_get_user_by_id_not_found(db_session: Session):
    service = UserService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.get_user_by_id(uuid.uuid4())
    assert exc_info.value.status_code == 404

## test update
def test_update_user_not_found(db_session: Session):
    service = UserService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.update_user(uuid.uuid4(), {"username": "new_username"})
    assert exc_info.value.status_code == 404 

## test delete user
def test_delete_user_not_found(db_session: Session):
    service = UserService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        service.delete_user(uuid.uuid4())
    assert exc_info.value.status_code == 404



def test_create_user_success(db_session):
    service = UserService(db_session)
    # The happy path: Everything is valid
    new_user = service.create_user(
        username="new_freelancer", 
        email="freelance@school.com", 
        password="SecurePassword123!", 
        role="student"
    )
    assert new_user is not None
    assert new_user.username == "new_freelancer"
    assert new_user.email == "freelance@school.com"
    # We ensure the password was hashed and NOT stored in plain text!
    assert new_user.password_hash != "SecurePassword123!"

def test_get_user_by_id_success(db_session, mock_teacher: User):
    service = UserService(db_session)
    # Testing retrieval of the fixture we built in conftest
    user = service.get_user_by_id(mock_teacher.id)
    assert user is not None
    assert user.email == "nguyen@abc.com"

def test_update_user_success(db_session, mock_teacher: User):
    service = UserService(db_session)
    # The happy path: Changing just the username
    updated_user = service.update_user(mock_teacher.id, {"username": "master_teacher"})
    assert updated_user.username == "master_teacher"
    # Ensure the email remained untouched!
    assert updated_user.email == "nguyen@abc.com"

def test_delete_user_success(db_session, mock_teacher: User):
    service = UserService(db_session)
    # The happy path: Successfully deleting the user
    result = service.delete_user(mock_teacher.id)
    assert result is True 
    
    # Verify they are actually gone from the database
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.get_user_by_id(mock_teacher.id)
    assert exc_info.value.status_code == 404





