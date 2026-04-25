import pytest 
from uuid import uuid4 
from schemas.student import StudentRead, StudentCreate, StudentUpdate 
from pydantic import ValidationError   

# --- FIXTURES ---
# These provide a clean, fresh ID for every test automatically
@pytest.fixture
def random_id():
    return uuid4()

@pytest.fixture
def valid_student_data(random_id):
    return {"name": "Nguyen Võ Thảo Nguyên", "classroom_id": random_id}

# --- TESTS ---

def test_create_student_success(valid_student_data):
    """Tests that valid data creates a student successfully"""
    student = StudentCreate(**valid_student_data)
    assert student.name == valid_student_data["name"]
    assert student.classroom_id == valid_student_data["classroom_id"]

@pytest.mark.parametrize("invalid_name", ["", "A"]) # Testing empty, 1 char, and 2 char
def test_create_student_name_constraints(invalid_name, random_id):
    """Tests various invalid name lengths in one go"""
    data = {"name": invalid_name, "classroom_id": random_id}
    with pytest.raises(ValidationError):
        StudentCreate(**data)        

def test_update_student_optional_fields(random_id):
    """Tests that we can update just one field if we want"""
    # Since it's an update, we might only want to change the name
    data = {"name": "New Name"}
    student = StudentUpdate(**data)
    assert student.name == "New Name"
    assert student.classroom_id is None # Update fields should be optional

def test_read_from_orm(random_id):
    """Tests that internal DB fields (secret_field) are filtered out"""
    class MockStudent:
        def __init__(self):
            self.id = uuid4()     
            self.name = "Nguyen Van A"
            self.classroom_id = random_id
            self.secret_field = "secret"

    # model_validate is the standard V2 way to convert DB objects to Schemas
    student = StudentRead.model_validate(MockStudent()) 

    assert student.name == "Nguyen Van A"
    assert hasattr(student, "id")
    assert not hasattr(student, "secret_field") # Ensures the "bouncer" did his job
