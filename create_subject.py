from db.models.user import User
from db.session import Sessionlocal
from repositories.user_repo import UserRepository
from db.models.user import User
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.subject import Subject 
from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore 
from repositories.subject_repo import SubjectRepository 


def create_subject():
    db = Sessionlocal()
    subject_repo = SubjectRepository(db)
    subject = subject_repo.create("Math") 
    print(f'Subject created: {subject}') 

if __name__ == "__main__":
    create_subject() 




