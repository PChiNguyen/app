from typing import List
from dataclasses import dataclass
from uuid import UUID 
from sqlalchemy import case, func
from sqlalchemy.orm import Session 
from db.models.student import Student
from db.models.student_score import Status

from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore
from sqlalchemy import case, func, cast, Numeric 

                                ## messi 

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
    def __init__(self,db: Session):
        self.db=db 
#### BUILDING THE FACTORY LEGO BLOCKS
    def _build_subject_averages_subquery(self, classroom_id: UUID, semester: int):
        # 1. THE CHEAT SHEET: Count the rules for every subject at once
        syllabus_counts = (
            self.db.query(
                AssessmentTemplate.subject_id.label("subject_id"),
                func.count(AssessmentTemplate.id).label("total_required")
            )
            .filter(AssessmentTemplate.semester == semester)
            .group_by(AssessmentTemplate.subject_id)
            .subquery() # Save it as a virtual table!
        )


        # 2. THE SMART STICKY NOTE (Now using the Cheat Sheet!)
        valid_sub_avg_calc = case(
            (func.count(StudentScore.id) == syllabus_counts.c.total_required, 
             # 🛠️ CAST ADDED HERE
             func.round(cast(func.sum(StudentScore.score * AssessmentTemplate.coefficient) / func.sum(AssessmentTemplate.coefficient), Numeric), 2)),
            else_=None
        )

        return (
            self.db.query(
                Student.id.label("student_id"),
                Student.name.label("student_name"),
                AssessmentTemplate.subject_id.label("subject_id"),
                valid_sub_avg_calc.label("sub_avg"),
                
                # 🚨 THE X-RAY COLUMNS (We expose the secret math!)
                func.count(StudentScore.id).label("completed_tests"),
                syllabus_counts.c.total_required.label("required_tests")
            )
            .join(StudentScore, Student.id == StudentScore.student_id)
            .join(AssessmentTemplate, StudentScore.assessment_template_id == AssessmentTemplate.id)
            
            # 3. WE JUST TAKE IT! Zip the Cheat Sheet into our main query!
            .join(syllabus_counts, AssessmentTemplate.subject_id == syllabus_counts.c.subject_id)
            
            .filter(
                Student.classroom_id == classroom_id,
                AssessmentTemplate.semester == semester,
                StudentScore.status == Status.GRADED
            )
            # 4. We have to add the total_required to the group_by to satisfy SQL rules
            .group_by(Student.id, AssessmentTemplate.subject_id, syllabus_counts.c.total_required) 
            .subquery()
        )
    
#🏭 The 5 Steps of the Magic Factory
#1. The Big Dump (JOIN)
#Instead of looking at things one by one, the factory robots take every student's backpack,
#  every teacher's rulebook, and the entire school's grading history, and dump it all onto one giant table. It’s a massive, crazy pile of papers.

#2. The Trash Can (WHERE / .filter)
#Before doing any math, a giant fan turns on and blows all the garbage off the table. Ungraded tests? Whoosh. Wrong semester? Whoosh. Broken rules? Whoosh. Into the trash they go. Only the perfect, finished test papers are left on the table.

#3. The Cubbies (GROUP BY)
#The robots sweep the good papers into little wooden cubbies. They put all of "Nguyên's Math papers" into one cubby, and all of "Lan's Physics papers" into another cubby. Everything is perfectly sorted.

#4. The Giant Smash (The Math)
#This is the coolest part. The robots do NOT read the papers one by one with a calculator. Instead, a giant hydraulic press drops from the ceiling and smashes down on all the cubbies at the exact same time. BAM! It instantly crushes the papers together and prints the final Average Score on the outside of the cubby box.

#5. The Delivery Box (SELECT / self.db.query)
#We don't mail a messy box full of crushed papers to your parents. The factory just looks at the outside of the cubby, copies your Name, Subject, and Final Score onto a beautiful, clean piece of paper, and mails only that to Python. The messy cubbies are thrown in the furnace.
    
    def _build_semester_gpa_subquery(self, classroom_id: UUID, semester: int):
        """LEGO BLOCK 2: Takes the Subject Averages and calculates the final Semester GPA"""
        
        # 1. Grab the Beautiful Table (Lego Block 1)
        sub_gpa_subquery = self._build_subject_averages_subquery(classroom_id, semester)

        # 2. The Smart Sticky Note (The Bouncer)
        valid_gpa_calc = case(
            (
                # If total subjects == valid graded subjects (No NULLs!)
                func.count(sub_gpa_subquery.c.subject_id) == func.count(sub_gpa_subquery.c.sub_avg), 
                # Then calculate the overall average!
                func.round(func.avg(sub_gpa_subquery.c.sub_avg), 2)
            ),
            else_=None
        )

# the case is like the if else statement in python, it checks if the count of subject_id (total subjects) is equal to the count of sub_avg (valid graded subjects).
#  If they are equal, it means all subjects have valid averages and we can calculate the overall average using func.avg. If they are not equal, it means at least one subject is missing a valid average, so we return NULL for the GPA. This way, we ensure that we only calculate the GPA when we have complete and valid data for all subjects!
## func.count(sub_gpa_subquery.c.sub_avg) with this, we dont need to create another subquery to count the valid subjects,
#  we can just count the non-NULL sub_avg directly in the same query! If they match, it means all subjects have valid averages and we can calculate the GPA.
#  If they don't match, it means at least one subject is missing a valid average, so we return NULL for the GPA. This way, we keep everything in one clean query without extra joins or subqueries!


        # 3. The Delivery Box (No extra joins needed!)
        return (
            self.db.query(
                sub_gpa_subquery.c.student_id,
                sub_gpa_subquery.c.student_name,
                valid_gpa_calc.label("semester_gpa")
            )
            # No .join() needed! We just read straight from Block 1
            # Fixed the Windsurf crash by adding student_name to the group_by!
            .group_by(
                sub_gpa_subquery.c.student_id, 
                sub_gpa_subquery.c.student_name
            )
            .subquery()
        )
    
    def _build_yearly_subject_averages_subquery(self, classroom_id: UUID):

        hk1_sq = self._build_subject_averages_subquery(classroom_id, semester=1).alias('hk1')
        hk2_sq = self._build_subject_averages_subquery(classroom_id, semester=2).alias('hk2')

## if we dont use the alias and try to join the two subqueries directly, we will have a problem because both subqueries have the same column names (student_id, student_name, subject_id, sub_avg).
## So we need to alias them to different names, like hk1 and hk2.

        yearly_calc = case(
            (   (hk1_sq.c.sub_avg != None) & (hk2_sq.c.sub_avg != None),
            func.round((hk1_sq.c.sub_avg + (hk2_sq.c.sub_avg * 2)) / 3, 2)
            ),
            else_=None) # If HK1 average exists, use it
        
        return (
            self.db.query(
                hk1_sq.c.student_id,
                hk1_sq.c.student_name,
                hk1_sq.c.subject_id,
                yearly_calc.label("yearly_sub_avg")
            )
            .join(hk2_sq,
                  (hk1_sq.c.student_id == hk2_sq.c.student_id) & 
                (hk1_sq.c.subject_id == hk2_sq.c.subject_id)
            )
            .subquery()
        )
    
    def _build_yearly_gpa_subquery(self, classroom_id: UUID):
        """LEGO BLOCK 4: Calculates the Final Yearly GPA (Cả Năm)"""
        
        # 1. Grab the Yearly Subject Averages (Lego Block 3)
        # This virtual table already contains the (HK1 + HK2*2)/3 math!
        yearly_sub_sq = self._build_yearly_subject_averages_subquery(classroom_id)

        # 2. The Smart Sticky Note (The Bouncer)
        # We use the exact same NULL-ignoring magic trick you discovered earlier!
        valid_yearly_gpa_calc = case(
            (
                # Did they get a valid Yearly Average for EVERY subject?
                func.count(yearly_sub_sq.c.subject_id) == func.count(yearly_sub_sq.c.yearly_sub_avg), 
                
                # If yes, calculate the overall GPA for the year!
                func.round(func.avg(yearly_sub_sq.c.yearly_sub_avg), 2)
            ),
            else_=None
        )

        # 3. The Delivery Box
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
    



    



            
        







### Now that we have our Lego Blocks, we can build the final masterpieces!


## SEMESTER AVERAGES AND GPAs


## CLASSROOM (FOR TEACHERS) VIEWS
    def get_classroom_all_subject_averages_by_semester(self, classroom_id: UUID, semester: int)->List[SubjectAverage]:
        """Fetches every single subject average for every student in the class."""
        
        # 1. Grab your masterpiece Lego Block 1
        sub_avg_query = self._build_subject_averages_subquery(classroom_id, semester)
        
     
        raw_rows = self.db.query(sub_avg_query).all()
        return [SubjectAverage(
            student_id=row.student_id,
            student_name=row.student_name,
            subject_id=row.subject_id,
            sub_avg=row.sub_avg,
            completed_tests=row.completed_tests,
            required_tests=row.required_tests,
        ) for row in raw_rows]
    
    def get_classroom_semester_gpas(self, classroom_id: UUID, semester: int)->List[SemesterGPA]:
        """Fetches the final Semester GPA for every student in the class."""
        
        # 1. Grab your masterpiece Lego Block 2
        gpa_query = self._build_semester_gpa_subquery(classroom_id, semester)
        
        # 2. Tell the Database to actually execute it and return the rows!
        raw_rows = self.db.query(gpa_query).all()
        return [SemesterGPA(
            student_id=row.student_id,
            student_name=row.student_name,
            semester_gpa=row.semester_gpa,
        ) for row in raw_rows]
    def get_classroom_yearly_subject_averages(self, classroom_id: UUID)->List[YearlySubjectAverage]:
        """Fetches every single subject average for the whole year (Cả Năm) for every student in the class."""
        
        # 1. Grab your masterpiece Lego Block 3
        yearly_sub_avg_query = self._build_yearly_subject_averages_subquery(classroom_id)

        raw_rows = self.db.query(yearly_sub_avg_query).all()
        return [YearlySubjectAverage(
            student_id=row.student_id,
            student_name=row.student_name,
            subject_id=row.subject_id,
            yearly_sub_avg=row.yearly_sub_avg,
        ) for row in raw_rows]
        
        
    def get_classroom_yearly_gpas(self, classroom_id: UUID)->List[YearlyGPA]:
        """Fetches the final Yearly GPA (Cả Năm) for every student in the class."""
        
        # 1. Grab your masterpiece Lego Block 4
        yearly_gpa_query = self._build_yearly_gpa_subquery(classroom_id)
        
        # 2. Tell the Database to actually execute it and return the rows!
        raw_rows = self.db.query(yearly_gpa_query).all()
        return [YearlyGPA(
            student_id=row.student_id,
            student_name=row.student_name,
            yearly_gpa=row.yearly_gpa,
        ) for row in raw_rows]



## STUDENT VIEWS
    def get_student_subject_averages_by_semester(self, classroom_id: UUID, student_id: UUID, semester: int)->SubjectAverage:
        """Fetches every single subject average for a specific student."""
        
        # 1. Grab your masterpiece Lego Block 1
        sub_avg_query = self._build_subject_averages_subquery(classroom_id, semester)
        
        # 2. Tell the Database to actually execute it and return the rows for just this student!
        raw_rows = self.db.query(sub_avg_query).filter(sub_avg_query.c.student_id == student_id).all()
        if raw_rows:
            return [SubjectAverage(
                student_id=row.student_id,
                student_name=row.student_name,
                subject_id=row.subject_id,
                sub_avg=row.sub_avg,
                completed_tests=row.completed_tests,
                required_tests=row.required_tests,
            ) for row in raw_rows]
        return None
    def get_student_semester_gpa(self, classroom_id: UUID, student_id: UUID, semester: int)->SemesterGPA:
        """Fetches the final Semester GPA for a specific student."""
        
        # 1. Grab your masterpiece Lego Block 2
        gpa_query = self._build_semester_gpa_subquery(classroom_id, semester)
        
        # 2. Tell the Database to actually execute it and return the row for just this student!
        raw_row = self.db.query(gpa_query).filter(gpa_query.c.student_id == student_id).first()
        if raw_row:
            return SemesterGPA(
                student_id=raw_row.student_id,
                student_name=raw_row.student_name,
                semester_gpa=raw_row.semester_gpa,
            )
        return None
    def get_student_yearly_subject_averages(self, classroom_id: UUID, student_id: UUID)->List[YearlySubjectAverage]:
        """Fetches every single subject average for the whole year (Cả Năm) for a specific student."""
        
        # 1. Grab your masterpiece Lego Block 3
        yearly_sub_avg_query = self._build_yearly_subject_averages_subquery(classroom_id)
        
        # 2. Tell the Database to actually execute it and return the rows for just this student!
        raw_rows = self.db.query(yearly_sub_avg_query).filter(yearly_sub_avg_query.c.student_id == student_id).all()
        if raw_rows:
            return [YearlySubjectAverage(
                student_id=row.student_id,
                student_name=row.student_name,
                subject_id=row.subject_id,
                yearly_sub_avg=row.yearly_sub_avg,
            ) for row in raw_rows]
        return None
    def get_student_yearly_gpa(self, classroom_id: UUID, student_id: UUID)->YearlyGPA:
        """Fetches the final Yearly GPA (Cả Năm) for a specific student."""
        
        # 1. Grab your masterpiece Lego Block 4
        yearly_gpa_query = self._build_yearly_gpa_subquery(classroom_id)
        
        # 2. Tell the Database to actually execute it and return the row for just this student!
        raw_row = self.db.query(yearly_gpa_query).filter(yearly_gpa_query.c.student_id == student_id).first()
        if raw_row:
            return YearlyGPA(
                student_id=raw_row.student_id,
                student_name=raw_row.student_name,
                yearly_gpa=raw_row.yearly_gpa,
            )
        return None

    




    
    
    
    

    
    

    
    
    
