# repositories/user_repo.py
from uuid import UUID
from typing import Any, Optional
from sqlalchemy import exists
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db.models.user import User
from core.security import get_password_hash
from core.exceptions import DatabaseValidationError


class UserRepository:
    def __init__(self, db: Session):
        self.db = db 

    def create(self, username: str, email: str, password: str, role: str) -> User:
        """
        Hashes the user's password and inserts a new User record into PostgreSQL safely.
        
        Args:
            username (str): Unique username for authentication.
            email (str): Unique email address.
            password (str): Plaintext password (will be hashed automatically).
            role (str): User role (e.g., 'admin', 'teacher', 'student').
        """
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except IntegrityError as e:
            self.db.rollback()  # 🛡️ Reset session on duplicate email or username
            raise DatabaseValidationError("A user with this email or username already exists.") from e
        except SQLAlchemyError as e:
            self.db.rollback()  # 🛡️ Reset session on general database error
            raise DatabaseValidationError("A database error occurred while creating the user account.") from e

    def get_by_id(self, user_id: Any) -> Optional[User]:
        """
        Fetches a user record by UUID or UUID string. Read-only.
        """
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None  # Invalid UUID string format
                
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Fetches a user record by email address. Read-only.
        """
        return self.db.query(User).filter(User.email == email).first()  

    def exists_by_email(self, email: str) -> bool:
        """
        Checks if an email exists in the database, returning True or False. Read-only.
        """
        return self.db.query(exists().where(User.email == email)).scalar()

    def delete(self, user_id: UUID) -> bool:
        """
        Deletes a user record by ID with transaction rollback protection.
        """
        user = self.get_by_id(user_id)
        if user:
            try:
                self.db.delete(user)
                self.db.commit()
                return True
            except SQLAlchemyError as e:
                self.db.rollback()  # 🛡️ Prevents session corruption on delete error
                raise DatabaseValidationError("Failed to delete user due to database constraints.") from e
        return False

    def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        """
        Updates specific attributes of a user record dynamically with transaction safety.
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                # Retains AttributeError behavior expected by unit tests
                raise AttributeError(f"User model has no attribute '{key}'")

        try:
            self.db.commit()
            self.db.refresh(user)   
            return user 
        except IntegrityError as e:
            self.db.rollback()  # 🛡️ Rollback on unique value conflict (e.g., email duplicate)
            raise DatabaseValidationError("Update failed because the email or username is already taken.") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseValidationError("A database error occurred while updating the user profile.") from e