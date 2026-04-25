from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID 
from typing import Optional

# 1. BASE: Common attributes (Safe to show the world)
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="A valid email address")       
    role: str = Field(default="student")

# 2. CREATE: This is what the user sends during Registration
class UserCreate(UserBase):
    # Only ask for the raw password here! Notice the max_length=50 to stop bcrypt errors!
    password: str = Field(..., min_length=8, max_length=50, description="Raw password from user")

# 3. READ: This is what we show the public
class UserRead(UserBase):
    id: UUID
    # Because password_hash is no longer in UserBase, it is TRULY hidden now!

    model_config = ConfigDict(from_attributes=True)

# 4. UPDATE: For changing profile info
class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(default=None, description="update user's email") 
    # Added max_length here too just to be safe!
    password: Optional[str] = Field(default=None, min_length=8, max_length=50, description="Raw password from user")