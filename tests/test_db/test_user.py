import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models.user import User, UserRole # Bây giờ nó sẽ hết lỗi
import pytest 
from sqlalchemy.exc import IntegrityError 
from sqlalchemy import text 
from db.models.user import User, UserRole  


def test_validate_username_too_short():
    with pytest.raises(ValueError) as exinfo:
        User(username="abc", email="abc@abc", password_hash="abc")
    assert "ít nhất 4 ký tự" in str(exinfo.value)

def test_validate_email_format():
    # thay vì ghi từng cái, mình sẽ dùng vòng lặp để test nhiều email không hợp lệ
    invalid_emails = ["annguyen", "an@gmail", "@gmail.com", "an..nguyen@gmail.com"]
    for email in invalid_emails:
        with pytest.raises(ValueError):
            User(username="validuser", email=email, password_hash="abc")
    

def test_validate_role_enum():
    """Test xem có ép kiểu string sang Enum tự động được không""" 
    u = User(username="admin_test", email="nguyen@gmail.com", password_hash="abc", role="student")
    assert u.role == UserRole.STUDENT 






## check ở database
def test_db_unique_username_constraint(db_session): 
    user1= User(username= "unique_user", email="unique1@abc.com", password_hash="abc")
    db_session.add(user1)
    db_session.commit()

    user2 = User(username="unique_user", email="unique2@abc.com", password_hash="abc")
    db_session.add(user2) 
    with pytest.raises(IntegrityError):
        db_session.commit() 

    db_session.rollback() 

def test_db_check_constraint_hacker(db_session):
    """Test dùng SQL thuần (Bind Parameters) để giả lập lách luật""" 
    sql=text("""
        INSERT INTO users (id, username, email, password_hash, role) 
        VALUES (:id, :u, :e, :p, :r)
    """)       
    data= {
        "id": "123e4567-e89b-12d3-a456-426614174000", 
        "u": "h", 
        "e": "hacker@abc", 
        "p": "abc", 
        "r": "student"  
    }
    with pytest.raises(IntegrityError):
        db_session.execute(sql, data)
        db_session.commit()   

    db_session.rollback()     

def test_vui(db_session):
    user = User(username="validuser", email="thaonguyen@gmail.com", password_hash="abc", role="student")
    print(str(user.id))

        
        



