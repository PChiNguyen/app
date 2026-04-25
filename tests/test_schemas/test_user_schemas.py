import pytest 
from schemas.user import UserCreate, UserRead, UserUpdate  
from pydantic import ValidationError 
from uuid import uuid4

def test_user_create_success():
    data={'username': "Nguyễn Võ Thảo Nguyên","email": "nguyen@gmail.com",'password_hash': "passwordhashsouoqwur", "password": "passwordhashsouoqwur", "role": "student"}
    user = UserCreate(**data)
    assert user.username == "Nguyễn Võ Thảo Nguyên"
    assert user.email == "nguyen@gmail.com"  
def test_user_create_fail():
    data={'username': "Nguyễn Võ Thảo Nguyên","email": "nguyen@gmail..", "password": "password", "role": "student"}
    with pytest.raises(ValidationError):
        UserCreate(**data) 

def test_user_update_success():
    data={'username': "Nguyễn Võ Thảo Nguyên","email": "nguyen@gmail.com", "password": "password", "role": "student"}
    user = UserUpdate(**data)
    assert user.username == "Nguyễn Võ Thảo Nguyên"
    assert user.email == "nguyen@gmail.com"   
def read_user_success():
    data={'username': "Nguyễn Võ Thảo Nguyên","email": "nguyen@gmail.com", "password": "password", "role": "student"}
    user = UserRead(**data)
    assert user.username == "Nguyễn Võ Thảo Nguyên"
    assert user.email == "nguyen@gmail.com"
def read_user_from_orm():
    class MockTeacher:
        id= uuid4()  
        username = "Nguyễn Võ Thảo Nguyên"
        email = "nguyen@gmail.com"
        password_hash= "password_hashhhh"

    user = UserRead.model_validate(MockTeacher())
    assert user.username == "Nguyễn Võ Thảo Nguyên"
    assert user.email == "nguyen@gmail.com" 
