import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.models.user import User
from db.models.student import Student
from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore, Status

# ==========================================
# 🏫 GROUP 1: CREATING SCORES (POST /)
# ==========================================
class TestCreateStudentScore:
    
    # 🟢 Happy Path
    def test_create_score_success(self, client: TestClient, db_session: Session, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate, mock_teacher: User):
        response = client.post("/api/scores/", json={
            "student_id": str(mock_student.id),
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 8.5
        })  
        assert response.status_code == 201 
        data = response.json()
        assert data["score"] == 8.5
        assert data["status"] == "graded" # Assuming your service auto-sets this!

    # 🔴 Sad Path
    def test_create_score_fake_student_returns_404(self, client: TestClient, db_session: Session, mock_assessment_template_semester1: AssessmentTemplate, mock_teacher: User):
        response = client.post("/api/scores/", json={
            "student_id": str(uuid4()), # Fake UUID
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 9.0
        })  
        assert response.status_code == 404

    # 🟡 Edge Case (Pydantic bounds check from your Schema)
    def test_create_score_out_of_bounds_returns_422(self, client: TestClient, db_session: Session, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate, mock_teacher: User):
        response = client.post("/api/scores/", json={
            "student_id": str(mock_student.id),
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 11.5 # 🚨 Edge case: Schema says le=10!
        })  
        assert response.status_code == 422


# ==========================================
# 🏫 GROUP 2: READING SCORES (GET)
# ==========================================
class TestReadStudentScores:

    # 🟢 Happy Path (Testing the Query Parameter!)
# 🟢 Happy Path (Testing the Path Parameter!)
    def test_read_scores_by_student_path_param(self, client: TestClient, db_session: Session, mock_student_score_semester1: StudentScore):
        # 🛠️ THE FIX: Use your new /student/{id} path!
        response = client.get(f"/api/scores/student/{str(mock_student_score_semester1.student_id)}")
        
        assert response.status_code == 200, f"Server crashed! Here is why: {response.text}" 
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    # 🟢 Happy Path
    def test_read_scores_by_template_id(self, client: TestClient, db_session: Session, mock_student_score_semester1: StudentScore):
        response = client.get(f"/api/scores/template/{mock_student_score_semester1.assessment_template_id}")
        assert response.status_code == 200
        assert response.json()[0]["assessment_template_id"] == mock_student_score_semester1.assessment_template_id

    # 🟢 Happy Path
    def test_read_scores_by_student_and_subject(self, client: TestClient, db_session: Session, mock_student_score_semester1: StudentScore):
        # We need the subject_id, which we get through the template relation
        subject_id = mock_student_score_semester1.assessment_template.subject_id
        response = client.get(f"/api/scores/student/{str(mock_student_score_semester1.student_id)}/subject/{subject_id}")
        assert response.status_code == 200


# ==========================================
# 🏫 GROUP 3: UPDATING SCORES (PUT /{score_id})
# ==========================================
'''class TestUpdateStudentScore:

    # 🟢 Happy Path
    def test_update_score_success(self, client: TestClient, db_session: Session, mock_student_score_semester1: StudentScore, mock_teacher: User):
        response = client.put(f"/api/scores/{str(mock_student_score_semester1.id)}", json={
            "score": 9.5
        })
        assert response.status_code == 200
        assert response.json()["score"] == 9.5

    # 🟡 Edge Case
    def test_update_score_negative_value_returns_422(self, client: TestClient, db_session: Session, mock_student_score_semester1: StudentScore, mock_teacher: User):
        response = client.put(f"/api/scores/{str(mock_student_score_semester1.id)}", json={
            "score": -2.0 # 🚨 Edge case: Schema says ge=0!
        })
        assert response.status_code == 422'''


# ==========================================
# 🏫 GROUP 4: DELETING SCORES (DELETE /{score_id})
# ==========================================
class TestDeleteStudentScore:

    # 🟢 Happy Path
    def test_delete_score_success(self, client: TestClient, db_session: Session, mock_student_score_semester1: StudentScore, mock_teacher: User):
        response = client.delete(f"/api/scores/{str(mock_student_score_semester1.id)}")
        assert response.status_code == 204

    # 🔴 Sad Path
    def test_delete_fake_score_returns_404(self, client: TestClient, db_session: Session, mock_teacher: User):
        response = client.delete(f"/api/scores/{str(uuid4())}")
        assert response.status_code == 404