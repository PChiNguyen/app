from typing import List
import os 
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict 

## Config is considered as a 'midfielder' between pydantic and environment variables, files and database
## Config is the middle layer between pydantic and environment variables, files and database
## Config is like a blueprint, it's like a template, awaiting to be filled by .env file, if settings find nothing
# in .env file, they will take default values as written below 

class Settings(BaseSettings):
    # 1. Basic Project Info 
    PROJECT_NAME: str = 'School Management System'
    API_V1_STR: str =  '/api/v1'

    # 2. Security (Critical for security.py)
    # In production, these MUST be overwritten in the .env file 
    SECRET_KEY: str = 'My_crush_is_Nguyen_Vo_Thao_Nguyen'
    ALGORITHM: str = 'HS256' 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 #  a week

    # 3. Database
    # Defaulting to SQLite for easy local development
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"   


    # 4. CORS (Cross-Origin Resource Sharing)
    # This allows your Frontend (like a React or PyQt5 app) to talk to the API
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [] 

    # 5. The "Magic" Link to the .env file
    # This tells Pydantic to look for a file named '.env' in your root folder

    model_config= SettingsConfigDict(env_file=".env.test" if os.getenv("TESTING") else ".env",
                                     env_file_encoding='utf-8',
                                     case_sensitive= True,
                                     extra ='ignore')

settings= Settings()








