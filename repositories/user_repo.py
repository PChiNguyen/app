from uuid import UUID 
from sqlalchemy import exists 
from sqlalchemy.orm import Session 
from db.models.user import User
from typing import Any, Optional
from core.security import get_password_hash  



class UserRepository:
    def __init__(self,db:Session):
        self.db=db 

    def create(self, username: str, email: str, password: str, role: str): # Take 'password', not 'password_hash'
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_by_id(self, user_id: Any):
        # If it's a string, turn it back into a UUID object
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None # Not a valid UUID, so user can't exist
                
        return self.db.query(User).filter(User.id == user_id).first()
    def get_by_email(self,email:str)->Optional[User]:
        
        return self.db.query(User).filter(User.email==email).first()  
    def exists_by_email(self,email:str)->bool:
        return self.db.query(exists().where(User.email==email)).scalar()
    ## Checking if a user with the given email exists, returning True or False.
    def delete(self,user_id:UUID)->bool:
        user=self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    ## Deleting a user by id, returning True if successful or False if the user was not found.
    def update(self,user_id:UUID,**kwargs)->Optional[User]:
        user= self.get_by_id(user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                # Now it will raise the error your test is looking for!
                raise AttributeError(f"User model has no attribute '{key}'")
        self.db.commit()
        self.db.refresh(user)   
        return user 
    ## Updating user attributes based on provided keyword arguments, returning the updated user object or None if the user was not found.   