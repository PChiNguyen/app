from pydantic import BaseModel  
from typing import Optional, List 
from uuid import UUID
## this file defines the token and token payload, it does nothing else 

class Token(BaseModel):
    access_token: str   
    token_type: str = "bearer"   


class TokenPayload(BaseModel):
    """The private data inside the 'envelope'."""
    sub: Optional[str] = None      # The User ID (Standard: subject)
    role: Optional[str] = None     # User category: 'admin', 'teacher', 'student'
    scopes: List[str] = []         # Specific actions: ["read:student", "edit:classroom"]
    exp: Optional[int] = None      # When this keycard stops working (Timestamp)


## So the when the user enters the app, they are given a token(a digital card), they can carry this around 
# due to the 'bearer' (portable), they tap their token to enter rooms(our files), then the files check the TokenPayload
# which is what is inside the token to decide if the user is allowed to enter, that's it !! 