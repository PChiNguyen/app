import uuid
from repositories.user_repo import UserRepository 
import pytest 
from core.security import create_access_token 
from api.deps import get_current_user   
from fastapi import HTTPException  



def test_get_current_user_success(db_session):
    user= UserRepository(db_session).create(
        username=f"user_{uuid.uuid4().hex[:6]}",
        email=f"user_{uuid.uuid4().hex[:6]}@example.com",
        password="secure_hash",
        role="student"
    )
    token = create_access_token(user.id)  # Create a token with a random user ID
    get_current_user(db=db_session, token=token)  # Should not raise an exception 

def test_get_current_user_fail(db_session):
    with pytest.raises(Exception) as exinfo:
        get_current_user(db=db_session, token="invalidtoken")
    print(exinfo)     
def test_get_current_user_non_existent_user(db_session):
    token = create_access_token(uuid.uuid4())  # Create a token with a random user ID that doesn't exist
    with pytest.raises(HTTPException) as exinfo:
        get_current_user(db=db_session, token=token)
    print(exinfo)
    assert exinfo.value.status_code == 404  
def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException) as exinfo: 
        get_current_user(db=db_session, token="thisisnotavalidtoken")
        
    assert exinfo.value.status_code == 403
    

    

