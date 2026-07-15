from fastapi.testclient import TestClient
import pytest


from repositories.user_repo import UserRepository
from core.security import get_password_hash
from sqlalchemy.orm import Session




def test_login_success(client: TestClient, db_session: Session):
    user_repo = UserRepository(db_session)
    
    user = user_repo.create(
        username="testuser",
        email="test@example.com",
        password="correct_password",
        role="STUDENT"
    )   
    
    
    # Force the database to write the data so the API can see it
    db_session.commit() 

    login_data = {
        "username": "test@example.com",
        "password": "correct_password"
    }
    
    response = client.post("/api/auth/login", data=login_data)
    
    # If this still gives 401, print the response to see the error message
    if response.status_code != 200:
        print(f"DEBUG: {response.json()}")
        
    assert response.status_code == 200

def test_login_wrong_password(client: TestClient):
    """Test that wrong password returns 401"""
    login_data = {
        "username": "test@example.com",##
        "password": "wrong_password"
    }
    response = client.post("/api/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"