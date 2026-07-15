import pytest 
from fastapi.testclient import TestClient
import uuid
from repositories.student_repo import StudentRepository 
from db.models.classroom import Classroom 
from db.models.student import Student 




def test_create_student(client: TestClient, db_session, mock_classroom: Classroom):
    response = client.post("/api/students/", json={
        "name": "Thảo Nguyên",
        "classroom_id": str(mock_classroom.id)
    })
    assert response.status_code == 201, f"Failed to create student: {response.json()}"
    assert response.json()["name"] == "Thảo Nguyên", f"Failed to create student: {response.json()}"
    assert response.json()["classroom_id"] == str(mock_classroom.id), f"Failed to create student: {response.json()}" 


def test_read_students(client: TestClient, db_session, mock_student: Student):
    response = client.get("/api/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Thảo Nguyên"
    assert response.json()[0]["id"] == str(mock_student.id)


def test_read_student(client: TestClient, db_session, mock_student):
    response = client.get(f"/api/students/{str(mock_student.id)}")
    assert response.status_code == 200
    assert response.json()["name"] == "Thảo Nguyên"
    assert response.json()["id"] == str(mock_student.id)


def test_update_student(client: TestClient, db_session, mock_student):
    response = client.put(f"/api/students/{str(mock_student.id)}", json={
        "name": "Updated Thảo Nguyên"
    })
    assert response.status_code == 200, f"Failed to update student: {response.json()}"
    assert response.json()["name"] == "Updated Thảo Nguyên"
    assert response.json()["id"] == str(mock_student.id)

def test_delete_student(client: TestClient, db_session, mock_student):
    delete_response = client.delete(f"/api/students/{str(mock_student.id)}")
    assert delete_response.status_code == 204, f"Failed to delete student: {delete_response.json()}"
    
    get_response = client.get(f"/api/students/{str(mock_student.id)}")
    assert get_response.status_code == 404, f"Expected 404 after deletion, got: {get_response.json()}"

## Additional tests for edge cases

def test_read_non_existent_student(client: TestClient, db_session):
    response = client.get(f"/api/students/{str(uuid.uuid4())}")
    assert response.status_code == 404, f"Expected 404 for non-existent student, got: {response.json()}"
