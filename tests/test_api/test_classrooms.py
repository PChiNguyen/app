import pytest
from fastapi.testclient import TestClient



from db.models.classroom import Classroom
from tests.conftest import MOCK_TEACHER_ID 
from sqlalchemy.orm import Session
from db.models.user import User 



## we cant simultaneously create a user and override the dependency to return that user, because the dependency override runs
#  before the test function, which means it runs before the user is created. This is why we need to use a fixture to create
#  the user first, and then have the dependency override return that user.

## fastapi doesnt know what is db_session, so we split our test 

# ==========================================
# FIX 2: A Cleaner Dependency Override
# ==========================================

# ==========================================
# THE supposed to be successful tests!
# ==========================================

def test_create_classroom(client: TestClient, db_session: Session, mock_teacher: User): # Pass db_session to trigger fixtures
    response = client.post("/api/classrooms/", json={
        "name": "Math",
        "teacher_id": str(mock_teacher.id),
        
    })
    
    # PRO-TIP: Print the error if it's not 201 so you don't get KeyErrors!
    assert response.status_code == 201, f"Failed: {response.json()}"
    
    data = response.json()
    assert data["name"] == "Math"
    
    assert "id" in data

def test_read_classrooms(client: TestClient, db_session: Session, mock_classroom):
    # This works now! mock_teacher is already in the DB thanks to the fixture.
  
    
    response = client.get("/api/classrooms/")   
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Science"
    
    # FIX 3: API responses are JSON strings, so convert the UUID to check it!


def test_delete_classroom(client: TestClient, db_session: Session, mock_classroom: Classroom):
    
    # Now, delete the classroom
    delete_response = client.delete(f"/api/classrooms/{str(mock_classroom.id)}")
    assert delete_response.status_code == 204, f"Failed to delete classroom: {delete_response.json()}"
    
    # Finally, check that it's really gone
    get_response = client.get(f"/api/classrooms/{str(mock_classroom.id)}")
    assert get_response.status_code == 404

def test_read_classroom(client: TestClient, db_session: Session, mock_classroom: Classroom):
    response = client.get(f"/api/classrooms/{str(mock_classroom.id)}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Science"
   
    
def test_update_classroom(client: TestClient, db_session: Session, mock_classroom: Classroom):
    response = client.put(f"/api/classrooms/{str(mock_classroom.id)}", json={
        "name": "Updated Science"
    })
    assert response.status_code == 200, f"Failed to update classroom: {response.json()}"
    
    data = response.json()
    assert data["name"] == "Updated Science"
  


## The failing tests 





