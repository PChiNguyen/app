from db.models.user import User
from db.session import Sessionlocal
from repositories.user_repo import UserRepository
from db.models.user import User
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.grade import Grade


# If you don't have a get_password_hash function yet, just use a raw string for now
# (But remember to hash it later when you build the real auth system!)
from core.security import get_password_hash 

def create_first_teacher():
    db = Sessionlocal()
    
    # 1. Check if the teacher already exists
    existing_user = db.query(User).filter(User.username == "thaonguyen7").first()
    if existing_user:
        print("Teacher already exists! Go log in.")
        return

    # 2. Create the Teacher
    # If your User model expects different fields, update these kwargs!
    repo= UserRepository(db)
    new_teacher= UserRepository.create(repo,username="thaonguyen7", email="thaonguyen7@abc.com",password='123456789',role="teacher")
    # 3. Save to SQLite
    
    print("✅ Teacher created successfully!")

if __name__ == "__main__":
    create_first_teacher()