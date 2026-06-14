import pytest
from uuid import uuid4, UUID
from db.models.user import User 

from pydantic import ValidationError
from schemas.classroom import ClassroomCreate, ClassroomRead

# --- FIXTURES ---
@pytest.fixture
def teacher_id():
    """Provides a fresh UUID for the teacher_id in every test"""
    return uuid4()

# --- TESTS ---

def test_create_classroom_success(mock_teacher: User):
    """Tests that a classroom is created with valid data"""
    data = {"name": "math", "teacher_id": mock_teacher.id}
    classroom = ClassroomCreate(**data)
    assert classroom.name == "math"
    

@pytest.mark.parametrize("invalid_name", [
    "",           # Empty string
    "A",          # Too short (assuming min_length=2)
    "A" * 51      # Too long (assuming max_length=50)
])
def test_create_classroom_invalid_name(invalid_name, teacher_id):
    """Tests name constraints using parametrization"""
    data = {"name": invalid_name, "teacher_id": teacher_id}
    with pytest.raises(ValidationError):
        ClassroomCreate(**data)

def test_read_classroom_from_orm(teacher_id):
    """Tests that StudentRead correctly filters DB objects"""
    class MockClassroom:
        def __init__(self):
            self.id = uuid4()
            self.name = "math"
            self.teacher_id = teacher_id
            self.internal_notes = "Top secret school notes" # Should be filtered out

    classroom = ClassroomRead.model_validate(MockClassroom())
    
    assert classroom.name == "math"
    assert hasattr(classroom, "id")
    # Ensure internal fields don't leak to the API
    assert not hasattr(classroom, "internal_notes")






