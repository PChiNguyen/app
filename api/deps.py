from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Correct paths based on your file names
from db.session import get_db
from core.config import settings
from db.models.user import User
from repositories.user_repo import UserRepository
from schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

## This is like the signpost, it stands at the entrance and ask for a token, if the user dont have a token
## they will be denied and asked to log in again in auth/login route 

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
)-> User:     
### Depends will run first and then run the function below
#### !!!!! big mistake, the Depends is actually an object itself, fastapi understands this but
## when we pass nothing in db, it will be like the default object isnt a session from get_db
## it's the Depends(get_db) object, so make sure you put in a session 
    try:
        payload= jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM] 
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError): 
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "Could not validate credentials"    

        )
    

    user_repo= UserRepository(db)
    user= user_repo.get_by_id(token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


