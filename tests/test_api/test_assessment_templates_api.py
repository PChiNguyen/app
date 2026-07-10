import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db.models.user import User
from db.models.subject import Subject
from db.models.assessment_template import AssessmentTemplate

# ==========================================
# 🏫 GROUP 1: CREATING TEMPLATES (POST /)
# ==========================================
class TestCreateAssessmentTemplate:
    
    # 🟢 1. The Happy Path
    def test_create_success(self, client: TestClient, db_session: Session, mock_subject: Subject, mock_teacher: User):
        response = client.post("/api/assessment-templates/", json={
            "subject_id": int(mock_subject.id),
            "name": "15 Minute Math",
            "type": "test", # Valid Enum String
            "coefficient": 1,
            "semester": 1
        })  
        assert response.status_code == 201 

    # 🔴 2. The Sad Path (Business Rule Violations)
    def test_create_fails_if_subject_does_not_exist(self, client: TestClient, db_session: Session, mock_teacher: User):
        # We pass Subject ID 99999, which we know doesn't exist in the DB!
        response = client.post("/api/assessment-templates/", json={
            "subject_id": 99999, 
            "name": "Ghost Test",
            "type": "test",
            "coefficient": 1,
            "semester": 1
        })  
        # Your service bouncer should catch this and throw a 404!
        assert response.status_code == 404 
        assert "not found" in response.json()["detail"].lower()

    # 🟡 3. The Edge Case (Pydantic Boundaries)
    def test_create_fails_with_invalid_enum_type(self, client: TestClient, db_session: Session, mock_subject: Subject, mock_teacher: User):
        response = client.post("/api/assessment-templates/", json={
            "subject_id": int(mock_subject.id),
            "name": "Hack Test",
            "type": "INVALID_GARBAGE_STRING", # The Pydantic Edge Case!
            "coefficient": 1,
            "semester": 1
        })  
        # FastAPI should block this at the door with a 422
        assert response.status_code == 422 


# ==========================================
# 🏫 GROUP 2: READING TEMPLATES (GET /{id})
# ==========================================
class TestReadAssessmentTemplate:

    # 🟢 1. The Happy Path
    def test_read_success(self, client: TestClient, db_session: Session, mock_assessment_template_semester1: AssessmentTemplate):
        response = client.get(f"/api/assessment-templates/{mock_assessment_template_semester1.id}")
        assert response.status_code == 200

    # 🔴 2. The Sad Path
    def test_read_non_existent_id_returns_404(self, client: TestClient, db_session: Session):
        # We query an ID that we know doesn't exist
        response = client.get("/api/assessment-templates/999999")
        assert response.status_code == 404


# ==========================================
# 🏫 GROUP 3: DELETING TEMPLATES (DELETE /{id})
# ==========================================
class TestDeleteAssessmentTemplate:

    # 🟢 1. The Happy Path
    def test_delete_success(self, client: TestClient, db_session: Session, mock_assessment_template_semester1: AssessmentTemplate):
        response = client.delete(f"/api/assessment-templates/{mock_assessment_template_semester1.id}")
        assert response.status_code == 204
        
        # Double check it actually died!
        get_response = client.get(f"/api/assessment-templates/{mock_assessment_template_semester1.id}")
        assert get_response.status_code == 404

    # 🔴 2. The Sad Path
    def test_delete_non_existent_id(self, client: TestClient, db_session: Session):
        response = client.delete("/api/assessment-templates/999999")
        assert response.status_code == 404