from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from db.models.user import UserRole 
from uuid import UUID 
from typing import Optional
import re 
def check_username_rules(username: str) -> str:
    username_clean = username.strip()
    if not username_clean:
        raise ValueError("Tên người dùng không được để trống")
    if username_clean.isdigit(): 
        raise ValueError("Tên người dùng không được chỉ chứa số")
    if not re.match(r"^\w+$", username_clean):
        raise ValueError("Tên người dùng chỉ được chứa chữ, số và dấu gạch dưới")
    return username_clean
def check_password_rules(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    if not re.match(password_regex, password):
        raise ValueError(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )
    return password


# 1. BASE: Common attributes (Safe to show the world)
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="A valid email address")       
    role: UserRole = Field(default=UserRole.STUDENT, description="User role: admin, teacher, or student")

## VALIDATING 
    @field_validator("username")
    @classmethod
    def validate_username_format(cls, username: str) -> str:
        return check_username_rules(username)
    


# 2. CREATE: This is what the user sends during Registration

class UserCreate(UserBase):
    password: str # The raw password from the user

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, password: str) -> str:
        return check_password_rules(password)

# 3. READ: This is what we show the public
class UserRead(UserBase):
    id: UUID
    # Because password_hash is no longer in UserBase, it is TRULY hidden now!

    model_config = ConfigDict(from_attributes=True)

# 4. UPDATE: For changing profile info
class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(default=None, description="update user's email") 
    password: Optional[str] = Field(default=None, min_length=8, max_length=50, description="Raw password from user")

    @field_validator("username")
    @classmethod
    def validate_optional_username(cls, username: Optional[str]) -> Optional[str]:
        if username is None:
            return None
        return check_username_rules(username)

    @field_validator("password")
    @classmethod
    def validate_optional_password(cls, password: Optional[str]) -> Optional[str]:
        if password is None:
            return None
        return check_password_rules(password) 
      