from unittest import result
from uuid import uuid4

import pytest 
from sqlalchemy.orm import Session
from db.models.student import Student
from repositories.grading_repo import GradingRepository, SemesterGPA, SubjectAverage, YearlyGPA, YearlySubjectAverage
from db.models.assessment_template import AssessmentTemplate

from db.models.student_score import StudentScore


## TESTING GRADING REPO METHODS FOR TEACHER'S VIEW 
def test_get_classroom_all_subject_averages_by_semester(db_session: Session, mock_student_score_semester1: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    results: list[SubjectAverage] = repo.get_classroom_all_subject_averages_by_semester(classroom_id = mock_student.classroom_id, semester = 1)
    result = results[0]
    assert result.student_id == mock_student.id
    assert result.student_name == mock_student.name
    assert result.sub_avg == mock_student_score_semester1.score

def test_get_classroom_semester_gpas(db_session: Session, mock_student_score_semester1: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    results: list[SemesterGPA] = repo.get_classroom_semester_gpas(classroom_id = mock_student.classroom_id, semester = 1)
    result = results[0]
    assert result.student_id == mock_student.id
    assert result.student_name == mock_student.name
    assert result.semester_gpa == mock_student_score_semester1.score

def test_get_classroom_yearly_subject_averages(db_session: Session, mock_student_score_semester1: StudentScore, mock_student_score_semester2: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    results: list[YearlySubjectAverage] = repo.get_classroom_yearly_subject_averages(classroom_id = mock_student.classroom_id)
    if results == []:
        raise AssertionError("Expected at least one result, got an empty list.")
    result = results[0]
    assert result.student_id == mock_student.id
    assert result.student_name == mock_student.name
    assert result.yearly_sub_avg == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3

def test_get_classroom_yearly_gpas(db_session: Session, mock_student_score_semester1: StudentScore, mock_student_score_semester2: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    results: list[YearlyGPA] = repo.get_classroom_yearly_gpas(classroom_id = mock_student.classroom_id)
    if results == []:
        raise AssertionError("Expected at least one result, got an empty list.")
    result = results[0]
    assert result.student_id == mock_student.id
    assert result.student_name == mock_student.name
    assert result.yearly_gpa == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3







### TESTING GRADING REPO METHODS FOR STUDENT'S VIEW
def test_get_student_subject_averages_by_semester(db_session: Session, mock_student_score_semester1: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    results: list[SubjectAverage] = repo.get_student_subject_averages_by_semester(classroom_id = mock_student.classroom_id,student_id = mock_student.id, semester = 1)
    assert results[0].student_id == mock_student.id
    assert results[0].student_name == mock_student.name
    assert results[0].sub_avg == mock_student_score_semester1.score

'''def test_get_student_semester_gpas(db_session: Session, mock_student_score_semester1: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    result: SemesterGPA = repo.get_student_semester_gpa(classroom_id = mock_student.classroom_id,student_id = mock_student.id, semester = 1)
    assert result.student_id == mock_student.id
    assert result.student_name == mock_student.name
    assert result.semester_gpa == mock_student_score_semester1.score'''

def test_get_student_yearly_subject_averages(db_session: Session, mock_student_score_semester1: StudentScore, mock_student_score_semester2: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    results: list[YearlySubjectAverage] = repo.get_student_yearly_subject_averages(classroom_id = mock_student.classroom_id, student_id = mock_student.id)
    assert results[0].student_id == mock_student.id
    assert results[0].student_name == mock_student.name
    assert results[0].yearly_sub_avg == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3

def test_get_student_yearly_gpas(db_session: Session, mock_student_score_semester1: StudentScore, mock_student_score_semester2: StudentScore, mock_student: Student):
    repo = GradingRepository(db_session)
    result: YearlyGPA = repo.get_student_yearly_gpa(classroom_id = mock_student.classroom_id, student_id = mock_student.id)
    assert result.student_id == mock_student.id
    assert result.student_name == mock_student.name
    assert result.yearly_gpa == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3

    assert result.student_id == mock_student.id 
    assert result.student_name == mock_student.name
    assert result.yearly_gpa == (mock_student_score_semester1.score + mock_student_score_semester2.score * 2) / 3










    
    

