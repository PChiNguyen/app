import pytest 
from schemas.user_schemas import UserCreate, UserRead, UserUpdate  
from pydantic import ValidationError 
from uuid import uuid4
@pytest.fixture 
def valid_user_data():
    return {"username": "thaonguyencute", "email": "nguyen@gmail.com", "password": "Nguyen71760309^^", "role": "student"}
def test_user_create_success(valid_user_data):
    user = UserCreate(**valid_user_data)
    assert user.username == "thaonguyencute"
    assert user.email == "nguyen@gmail.com"  
def test_user_create_fail(valid_user_data):
    data={'username': "Nguyễn Võ Thảo Nguyên","email": "nguyen@gmail..", "password": "password", "role": "student"}
    with pytest.raises(ValidationError):
        UserCreate(**data) 

def test_user_update_success():
    new_data={'username': "thaonguyendangiu","email": "nguyen@gmail.com", "password": "Nguyen71760309^^", "role": "student"}
    user = UserUpdate(**new_data)
    assert user.username == "thaonguyendangiu"
    assert user.email == "nguyen@gmail.com"   
def read_user_success(valid_user_data):
    user = UserRead(**valid_user_data)
    assert user.username == "thaonguyencute"
    assert user.email == "nguyen@gmail.com"
def read_user_from_orm():
    class MockTeacher:
        id= uuid4()  
        username = "thaonguyendangiu"
        email = "nguyen@gmail.com"
        password_hash= "password_hashhhh"

    user = UserRead.model_validate(MockTeacher())
    assert user.username == "thaonguyendangiu"
    assert user.email == "nguyen@gmail.com" 
