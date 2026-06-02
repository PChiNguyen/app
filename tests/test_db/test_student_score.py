import sys
import os
import uuid

from db.models.subject import Subject
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
import pytest
from sqlalchemy.exc import IntegrityError   
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.models.student_score import StudentScore
from db.models.assessment_template import AssessmentTemplate
from db.models.student import Student 


def test_student_score_validation_all_cases(db_session: Session, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
    # invalid score 
    with pytest.raises(ValueError):
        StudentScore(student_id= mock_student.id, assessment_template_id= mock_assessment_template_semester1.id, score= -1)  # Điểm âm
    #invalid status 
    with pytest.raises(ValueError):
        StudentScore(student_id= mock_student.id,
                      assessment_template_id= mock_assessment_template_semester1.id,
                        score= 10, status= "Completed") 
    # invalid assessment_template_id
    with pytest.raises(ValueError):        
        StudentScore(student_id= mock_student.id,
                      assessment_template_id= uuid.uuid4(),
                        score= 10)
    # invalid student_id
    with pytest.raises(ValueError):        
        StudentScore(student_id= 11,
                      assessment_template_id= mock_assessment_template_semester1.id,
                        score= 10)
        
def test_hacker_insert_invalid_student_score(db_session: Session, mock_student: Student, mock_assessment_template_semester1: AssessmentTemplate):
    sql= text("""INSERT INTO student_scores(id, student_id, assessment_template_id, score, status)
              VALUES(:id,:student_id,:template_id,:score,:status)""")
    data= {
        'id': str(uuid.uuid4()),
        'student_id': str(mock_student.id),
        'template_id': str(mock_assessment_template_semester1.id),
        'score': 15, # điểm không hợp lệ nhưng sẽ được chèn thẳng vào DB
        'status': 'Completed' # status không hợp lệ nhưng sẽ được chèn thẳng vào DB
    }
    with pytest.raises(IntegrityError) as e:
        db_session.execute(sql,data)
        db_session.commit()
    print(f'{e}')

    db_session.rollback()


# test relationships 


  


