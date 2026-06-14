from repositories.user_repo import UserRepository
from repositories.classroom_repo import ClassroomRepository
from sqlalchemy.orm import Session
from fastapi import HTTPException  

from schemas.user_schemas import UserUpdate 



class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.classroom_repo = ClassroomRepository(db)
    
    def create_user(self, username: str, email: str, password: str, role: str):
        if self.user_repo.exists_by_email(email):
            raise HTTPException(status_code=400, detail="Email already registered")
        return self.user_repo.create(username, email, password, role) 
        
    
    def get_user_by_id(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    def update_user(self, user_id, updates: UserUpdate):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        

        return self.user_repo.update(user_id, **updates)
    
    def delete_user(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self.user_repo.delete(user_id)
    
    