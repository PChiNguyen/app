import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.models.user import User
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.assessment_template import AssessmentTemplate

# ==========================================
# 🛑 GROUP 1: THE EMPTY STATE (SAD PATH)
# Proving your Service Layer catches empty lists!
# ==========================================
class TestGradingEmptyState:

    def test_empty_classroom_subject_averages_returns_404(self, client: TestClient, mock_classroom: Classroom):
        # The DB has no scores, so it MUST return 404 based on your service logic
        response = client.get(f"/api/grading/classrooms/{str(mock_classroom.id)}/semesters/1/subject-averages")
        assert response.status_code == 404
        assert "No grades found" in response.json()["detail"]
    @pytest.mark.redis
    def test_empty_student_semester_gpa_returns_404(self, client: TestClient, mock_classroom: Classroom, mock_student: Student):
        response = client.get(f"/api/grading/classrooms/{str(mock_classroom.id)}/students/{str(mock_student.id)}/semesters/1/gpa")
        assert response.status_code == 404


# ==========================================
# 🟢 GROUP 2: THE POPULATED STATE (HAPPY PATH)
# Seeding the database to prove the Math works!
# ==========================================
class TestGradingPopulatedState:
    @pytest.mark.redis
    def test_populated_student_semester_gpa_success(self, client: TestClient, db_session: Session, mock_classroom: Classroom, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
        
        # 1. ACTIVATE THE DB: We must manually insert a score so the Repo has data!
        post_response = client.post("/api/scores/", json={
            "student_id": str(mock_student.id),
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 9.5
        })
        assert post_response.status_code == 201 # Verify seed worked

        # 2. RUN THE GRADING REPORT
        response = client.get(f"/api/grading/classrooms/{str(mock_classroom.id)}/students/{str(mock_student.id)}/semesters/1/gpa")

        # 3. VERIFY SUCCESS
        assert response.status_code == 200
        data = response.json()
        assert "semester_gpa" in data
        assert data["semester_gpa"] == 9.5

    def test_populated_classroom_subject_averages_success(self, client: TestClient, db_session: Session, mock_classroom: Classroom, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
        
        # 1. Seed data
        client.post("/api/scores/", json={
            "student_id": str(mock_student.id),
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 8.0
        })

        # 2. Call the bulk classroom report
        response = client.get(f"/api/grading/classrooms/{str(mock_classroom.id)}/semesters/1/subject-averages")

        # 3. Verify
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1
        assert response.json()[0]["sub_avg"] == 8.0