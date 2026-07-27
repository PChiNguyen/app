from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID 

from sqlalchemy import case, func, cast, Numeric
from sqlalchemy.orm import Session 
from core.cache_decorator import cache_response

from db.models.student import Student
from db.models.student_score import StudentScore, Status
from db.models.assessment_template import AssessmentTemplate


@dataclass 
class SubjectAverage:
    student_id: UUID
    student_name: str
    subject_id: int
    sub_avg: float
    completed_tests: int
    required_tests: int

@dataclass
class SemesterGPA:
    student_id: UUID
    student_name: str
    semester_gpa: float

@dataclass
class YearlySubjectAverage:
    student_id: UUID
    student_name: str
    subject_id: int
    yearly_sub_avg: float

@dataclass
class YearlyGPA:
    student_id: UUID
    student_name: str
    yearly_gpa: float


class GradingRepository:
    def __init__(self, db: Session):
        self.db = db 

    # ==========================================
    # SUBQUERY BUILDING LEGO BLOCKS (READ-ONLY)
    # ==========================================
    def _build_subject_averages_subquery(self, classroom_id: UUID, semester: int):
        syllabus_counts = (
            self.db.query(
                AssessmentTemplate.subject_id.label("subject_id"),
                func.count(AssessmentTemplate.id).label("total_required")
            )
            .filter(AssessmentTemplate.semester == semester)
            .group_by(AssessmentTemplate.subject_id)
            .subquery()
        )

        valid_sub_avg_calc = case(
            (
                func.count(StudentScore.id) == syllabus_counts.c.total_required, 
                func.round(cast(func.sum(StudentScore.score * AssessmentTemplate.coefficient) / func.sum(AssessmentTemplate.coefficient), Numeric), 2)
            ),
            else_=None
        )

        return (
            self.db.query(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                AssessmentTemplate.subject_id.label("subject_id"),
                valid_sub_avg_calc.label("sub_avg"),
                func.count(StudentScore.id).label("completed_tests"),
                syllabus_counts.c.total_required.label("required_tests")
            )
            .join(StudentScore, Student.id == StudentScore.student_id)
            .join(AssessmentTemplate, StudentScore.assessment_template_id == AssessmentTemplate.id)
            .join(syllabus_counts, AssessmentTemplate.subject_id == syllabus_counts.c.subject_id)
            .filter(
                Student.classroom_id == classroom_id,
                AssessmentTemplate.semester == semester,
                StudentScore.status == Status.GRADED
            )
            .group_by(Student.id, AssessmentTemplate.subject_id, syllabus_counts.c.total_required) 
            .subquery()
        )

    def _build_semester_gpa_subquery(self, classroom_id: UUID, semester: int):
        sub_gpa_subquery = self._build_subject_averages_subquery(classroom_id, semester)

        valid_gpa_calc = case(
            (
                func.count(sub_gpa_subquery.c.subject_id) == func.count(sub_gpa_subquery.c.sub_avg), 
                func.round(func.avg(sub_gpa_subquery.c.sub_avg), 2)
            ),
            else_=None
        )

        return (
            self.db.query(
                sub_gpa_subquery.c.student_id,
                sub_gpa_subquery.c.student_name,
                valid_gpa_calc.label("semester_gpa")
            )
            .group_by(
                sub_gpa_subquery.c.student_id, 
                sub_gpa_subquery.c.student_name
            )
            .subquery()
        )

    def _build_yearly_subject_averages_subquery(self, classroom_id: UUID):
        hk1_sq = self._build_subject_averages_subquery(classroom_id, semester=1).alias('hk1')
        hk2_sq = self._build_subject_averages_subquery(classroom_id, semester=2).alias('hk2')

        yearly_calc = case(
            (
                (hk1_sq.c.sub_avg != None) & (hk2_sq.c.sub_avg != None),
                func.round((hk1_sq.c.sub_avg + (hk2_sq.c.sub_avg * 2)) / 3, 2)
            ),
            else_=None
        )

        return (
            self.db.query(
                hk1_sq.c.student_id,
                hk1_sq.c.student_name,
                hk1_sq.c.subject_id,
                yearly_calc.label("yearly_sub_avg")
            )
            .join(
                hk2_sq,
                (hk1_sq.c.student_id == hk2_sq.c.student_id) & 
                (hk1_sq.c.subject_id == hk2_sq.c.subject_id)
            )
            .subquery()
        )

    def _build_yearly_gpa_subquery(self, classroom_id: UUID):
        yearly_sub_sq = self._build_yearly_subject_averages_subquery(classroom_id)

        valid_yearly_gpa_calc = case(
            (
                func.count(yearly_sub_sq.c.subject_id) == func.count(yearly_sub_sq.c.yearly_sub_avg), 
                func.round(func.avg(yearly_sub_sq.c.yearly_sub_avg), 2)
            ),
            else_=None
        )

        return (
            self.db.query(
                yearly_sub_sq.c.student_id,
                yearly_sub_sq.c.student_name,
                valid_yearly_gpa_calc.label("yearly_gpa")
            )
            .group_by(
                yearly_sub_sq.c.student_id, 
                yearly_sub_sq.c.student_name
            )
            .subquery()
        )

    # ==========================================
    # CLASSROOM VIEWS
    # ==========================================
    @cache_response(prefix="gpa:classroom_subject_averages", ttl=3600)
    def get_classroom_all_subject_averages_by_semester(self, classroom_id: UUID, semester: int) -> List[SubjectAverage]:
        sub_avg_query = self._build_subject_averages_subquery(classroom_id, semester)
        raw_rows = self.db.query(sub_avg_query).all()
        return [
            SubjectAverage(
                student_id=row.student_id,
                student_name=row.student_name,
                subject_id=row.subject_id,
                sub_avg=row.sub_avg,
                completed_tests=row.completed_tests,
                required_tests=row.required_tests,
            ) for row in raw_rows
        ]

    @cache_response(prefix="gpa:classroom_semester_gpas", ttl=3600)
    def get_classroom_semester_gpas(self, classroom_id: UUID, semester: int) -> List[SemesterGPA]:
        gpa_query = self._build_semester_gpa_subquery(classroom_id, semester)
        raw_rows = self.db.query(gpa_query).all()
        return [
            SemesterGPA(
                student_id=row.student_id,
                student_name=row.student_name,
                semester_gpa=row.semester_gpa,
            ) for row in raw_rows
        ]

    @cache_response(prefix="gpa:classroom_yearly_subject_averages", ttl=3600)
    def get_classroom_yearly_subject_averages(self, classroom_id: UUID) -> List[YearlySubjectAverage]:
        yearly_sub_avg_query = self._build_yearly_subject_averages_subquery(classroom_id)
        raw_rows = self.db.query(yearly_sub_avg_query).all()
        return [
            YearlySubjectAverage(
                student_id=row.student_id,
                student_name=row.student_name,
                subject_id=row.subject_id,
                yearly_sub_avg=row.yearly_sub_avg,
            ) for row in raw_rows
        ]

    @cache_response(prefix="gpa:classroom_yearly_gpas", ttl=3600)
    def get_classroom_yearly_gpas(self, classroom_id: UUID) -> List[YearlyGPA]:
        yearly_gpa_query = self._build_yearly_gpa_subquery(classroom_id)
        raw_rows = self.db.query(yearly_gpa_query).all()
        return [
            YearlyGPA(
                student_id=row.student_id,
                student_name=row.student_name,
                yearly_gpa=row.yearly_gpa,
            ) for row in raw_rows
        ]

    # ==========================================
    # STUDENT VIEWS
    # ==========================================
    @cache_response(prefix="gpa:student_subject_averages", ttl=3600)
    def get_student_subject_averages_by_semester(self, classroom_id: UUID, student_id: UUID, semester: int) -> Optional[List[SubjectAverage]]:
        sub_avg_query = self._build_subject_averages_subquery(classroom_id, semester)
        raw_rows = self.db.query(sub_avg_query).filter(sub_avg_query.c.student_id == student_id).all()
        if raw_rows:
            return [
                SubjectAverage(
                    student_id=row.student_id,
                    student_name=row.student_name,
                    subject_id=row.subject_id,
                    sub_avg=row.sub_avg,
                    completed_tests=row.completed_tests,
                    required_tests=row.required_tests,
                ) for row in raw_rows
            ]
        return None

    @cache_response(prefix="gpa:student_semester_gpa", ttl=3600)
    def get_student_semester_gpa(self, classroom_id: UUID, student_id: UUID, semester: int) -> Optional[SemesterGPA]:
        gpa_query = self._build_semester_gpa_subquery(classroom_id, semester)
        raw_row = self.db.query(gpa_query).filter(gpa_query.c.student_id == student_id).first()
        if raw_row:
            return SemesterGPA(
                student_id=raw_row.student_id,
                student_name=raw_row.student_name,
                semester_gpa=raw_row.semester_gpa,
            )
        return None

    @cache_response(prefix="gpa:student_yearly_subject_averages", ttl=3600)
    def get_student_yearly_subject_averages(self, classroom_id: UUID, student_id: UUID) -> Optional[List[YearlySubjectAverage]]:
        yearly_sub_avg_query = self._build_yearly_subject_averages_subquery(classroom_id)
        raw_rows = self.db.query(yearly_sub_avg_query).filter(yearly_sub_avg_query.c.student_id == student_id).all()
        if raw_rows:
            return [
                YearlySubjectAverage(
                    student_id=row.student_id,
                    student_name=row.student_name,
                    subject_id=row.subject_id,
                    yearly_sub_avg=row.yearly_sub_avg,
                ) for row in raw_rows
            ]
        return None

    @cache_response(prefix="gpa:student_yearly_gpa", ttl=3600)
    def get_student_yearly_gpa(self, classroom_id: UUID, student_id: UUID) -> Optional[YearlyGPA]:
        yearly_gpa_query = self._build_yearly_gpa_subquery(classroom_id)
        raw_row = self.db.query(yearly_gpa_query).filter(yearly_gpa_query.c.student_id == student_id).first()
        if raw_row:
            return YearlyGPA(
                student_id=raw_row.student_id,
                student_name=raw_row.student_name,
                yearly_gpa=raw_row.yearly_gpa,
            )
        return None