import pytest 

from core.security import verify_password, get_password_hash, create_access_token 

def test_get_password_hash():
    hashed_password= get_password_hash("123456789")
    assert verify_password("123456789", hashed_password)  
    assert not verify_password("password1", hashed_password)
## this thing simultaneously tests the two functions 

def test_create_access_token_fail():
    with pytest.raises(Exception) as exinfo:
        create_access_token()
    print(exinfo)

    ## we can use pytest.mark.parametrize here to test multiple inputs
def test_create_access_token_success():
    token= create_access_token("testuser")
    assert token 
    print(f'Token: {token}')










