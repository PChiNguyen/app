from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.deps import get_current_user
from db.session import get_db
from core import security
from core.config import settings
from repositories.user_repo import UserRepository
from schemas.auth import Token
from schemas.user_schemas import UserRead 

router= APIRouter() 


@router.post('/login', response_model= Token)
## this response_model ensures that the response from this endpoint will be in the format of the Token schema defined in schemas/auth.py
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
## This form_data tells FastAPI to look at the request and find two specific fields: username and password.


    user_repo= UserRepository(db)
    user= user_repo.get_by_email(email= form_data.username) ## this is to check if the user exists
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect email or password"
        )
    access_token_expires= timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(subject= str(user.id),
                                                      expires_delta= access_token_expires),
                                                      'token_type': "bearer"
    }
@router.get('/me', response_model= UserRead)
def read_users_me(
    current_user= Depends(get_current_user)
):
    return current_user

        

    
      
