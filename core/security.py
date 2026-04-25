from datetime import datetime, timedelta, timezone 
from typing import Optional, Union, Any 
from jose import jwt 
from passlib.context import CryptContext 
from core.config import settings 




import bcrypt


# DELETE the passlib CryptContext stuff entirely!

def get_password_hash(password: str) -> str:
    # 1. Convert string to bytes
    # 2. Hash it with a salt
    # 3. Decode back to string for the database
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Convert both the typed password and the database hash into bytes to compare them
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

# Keep your create_access_token function exactly the way it is below here!

'''pwd_context= CryptContext(schemes= ["bcrypt"], deprecated="auto",
    bcrypt__truncate_error=False,bcrypt__ident="2b")'''
## the problem is the bcrypt version 
## this is actually an object of CryptContext class
## schemes is a list of hashing algorithms to be used
## it's like disposable, perhaps it will be replaced in the future 


'''def get_password_hash(password: str):
    print("\n--- DEBUG START ---")
    print(f"TYPE: {type(password)}")
    print(f"VALUE: {password}")
    print(f"LENGTH: {len(str(password))}")
    print("--- DEBUG END ---\n")
    hashed_password = pwd_context.hash(password)
    print(f'Hashed password: {hashed_password}')
    return hashed_password


## this will be called by our create_user function 
def verify_password(plain_pasword: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_pasword, hashed_password) 
## this will be called when the user log in, like when i type my name on facebook, the app will search
# for my name in its db, get the hashed password and compare it with the one i type '''

# 2. Setup JWT Generation (The 'Keycard Machine') 
def create_access_token(subject: Union[str, Any],
                         expires_delta: Optional[timedelta] = None) -> str:
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Pulls the default 'Backup' value from your config.py
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # The Payload: The 'Letter' inside the envelope
    to_encode = {
        "exp": expire, 
        "sub": str(subject)  # 'sub' is standard for User ID
    }
    
    # The Signature: Sealing the envelope with our SECRET_KEY
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    ## this is considered the anti-counterfeit stamp of the envelope(token)
    
    return encoded_jwt
    




