import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from db.models.classroom import Classroom
from db.models.student import Student
from db.models.assessment_template import AssessmentTemplate

# ==========================================
# 🛑 GROUP 1: THE EMPTY STATE (SAD PATH)
# Kiểm tra API trả về 404 khi chưa có dữ liệu điểm
# ==========================================
class TestGradingEmptyState:

    def test_empty_classroom_subject_averages_returns_404(
        self, client: TestClient, mock_classroom: Classroom
    ):
        """Kiểm tra khi lớp chưa có điểm thì trả về lỗi 404 và đúng thông báo."""
        # 1. Gọi API lấy điểm trung bình môn của lớp khi chưa có điểm
        response = client.get(
            f"/api/grading/classrooms/{str(mock_classroom.id)}/semesters/1/subject-averages"
        )
        
        # 2. Kiểm tra Response
        assert response.status_code == 404
        assert "No subject averages found" in response.json()["detail"]

    @pytest.mark.redis
    def test_empty_student_semester_gpa_returns_404(
        self, client: TestClient, mock_classroom: Classroom, mock_student: Student
    ):
        """Kiểm tra khi học sinh chưa có điểm thì lấy GPA cá nhân sẽ trả về 404."""
        # 1. Gọi API GPA cá nhân (Đã sửa URL khớp với Router)
        response = client.get(
            f"/api/grading/classroom/{str(mock_classroom.id)}/student/{str(mock_student.id)}/semester/1/gpa"
        )
        
        # 2. Kiểm tra Response
        assert response.status_code == 404
        assert "Student GPA record not found" in response.json()["detail"]


# ==========================================
# 🟢 GROUP 2: THE POPULATED STATE (HAPPY PATH)
# Thêm dữ liệu mẫu vào DB và kiểm tra tính chính xác của API
# ==========================================
class TestGradingPopulatedState:

    @pytest.mark.redis
    def test_populated_student_semester_gpa_success(
        self, 
        client: TestClient, 
        db_session: Session, 
        mock_classroom: Classroom, 
        mock_student: Student, 
        mock_assessment_template_semester1: AssessmentTemplate
    ):
        """Thêm điểm mẫu và kiểm tra API trả về GPA học kỳ chính xác."""
        # 1. CHÈN ĐIỂM MẪU: Thêm 1 con điểm 9.5 cho học sinh
        post_response = client.post("/api/scores/", json={
            "student_id": str(mock_student.id),
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 9.5
        })
        assert post_response.status_code == 201  # Xác nhận đã chèn điểm thành công

        # 2. GỌI API LẤY GPA HỌC KỲ CÁ NHÂN
        response = client.get(
            f"/api/grading/classroom/{str(mock_classroom.id)}/student/{str(mock_student.id)}/semester/1/gpa"
        )

        # 3. KIỂM TRA KẾT QUẢ
        assert response.status_code == 200
        data = response.json()
        assert "semester_gpa" in data
        assert data["semester_gpa"] == 9.5

    def test_populated_classroom_subject_averages_success(
        self, 
        client: TestClient, 
        db_session: Session, 
        mock_classroom: Classroom, 
        mock_student: Student, 
        mock_assessment_template_semester1: AssessmentTemplate
    ):
        """Thêm điểm mẫu và kiểm tra API trả về danh sách điểm trung bình môn toàn lớp."""
        # 1. Chèn điểm mẫu 8.0
        client.post("/api/scores/", json={
            "student_id": str(mock_student.id),
            "assessment_template_id": mock_assessment_template_semester1.id,
            "score": 8.0
        })

        # 2. Gọi API lấy điểm trung bình môn toàn lớp
        response = client.get(
            f"/api/grading/classrooms/{str(mock_classroom.id)}/semesters/1/subject-averages"
        )

        # 3. Kiểm tra kết quả
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1
        assert response.json()[0]["sub_avg"] == 8.0