import pytest
from fastapi.testclient import TestClient

from db.models.grade import Grade
from repositories.grade_repo import GradeRepository

from tests.conftest import MOCK_TEACHER_ID 



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

def test_create_classroom(client: TestClient, db_session): # Pass db_session to trigger fixtures
    response = client.post("/api/classrooms/", json={
        "name": "Math"
    })
    
    # PRO-TIP: Print the error if it's not 201 so you don't get KeyErrors!
    assert response.status_code == 201, f"Failed: {response.json()}"
    
    data = response.json()
    assert data["name"] == "Math"
    
    assert "id" in data

def test_read_classrooms(client: TestClient, db_session, mock_classroom):
    # This works now! mock_teacher is already in the DB thanks to the fixture.
  
    
    response = client.get("/api/classrooms/")   
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Science"
    
    # FIX 3: API responses are JSON strings, so convert the UUID to check it!


def test_delete_classroom(client: TestClient, db_session, mock_classroom):
    
    # Now, delete the classroom
    delete_response = client.delete(f"/api/classrooms/{str(mock_classroom.id)}")
    assert delete_response.status_code == 204, f"Failed to delete classroom: {delete_response.json()}"
    
    # Finally, check that it's really gone
    get_response = client.get(f"/api/classrooms/{str(mock_classroom.id)}")
    assert get_response.status_code == 404

def test_read_classroom(client: TestClient, db_session, mock_classroom):
    response = client.get(f"/api/classrooms/{str(mock_classroom.id)}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Science"
   
    
def test_update_classroom(client: TestClient, db_session, mock_classroom):
    response = client.put(f"/api/classrooms/{str(mock_classroom.id)}", json={
        "name": "Updated Science"
    })
    assert response.status_code == 200, f"Failed to update classroom: {response.json()}"
    
    data = response.json()
    assert data["name"] == "Updated Science"
  


## The failing tests 




    
def test_get_classroom_ranking(client: TestClient, db_session, mock_classroom,mock_student_grades):
    response = client.get(f"/api/classrooms/{str(mock_classroom.id)}/ranking")
    assert response.status_code == 200, f"Failed to get classroom ranking: {response.json()}"
    data = response.json()
    assert isinstance(data, list), f"Expected a list of students with GPA, got: {data}"
    assert len(data) == 1, f"Expected 1 student in the classroom, got: {len(data)}"
    assert data[0]["name"] == "Thảo Nguyên", f"Expected student name to be 'Thảo Nguyên', got: {data[0]['name']}"
    assert data[0]["gpa"] == (8.5 + 9.0) / 2, f"Expected GPA to be 8.75, got: {data[0]['gpa']}"

