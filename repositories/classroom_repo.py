
from uuid import UUID 
from sqlalchemy import func 
from db.models.assessment_template import AssessmentTemplate
from db.models.classroom import Classroom
from sqlalchemy.orm import Session
from typing import List, NamedTuple, Optional   
from db.models.student import Student
from db.models.student import Student
from db.models.student_score import Status, StudentScore
from dataclasses import dataclass

class LeaderboardRow(NamedTuple): 
    student_id: UUID
    student_name: str
    gpa: float
    class_rank: int
class ClassroomRepository:
    def __init__(self,db:Session):
        self.db=db

    def create(self,name:str,teacher_id:UUID)->Classroom:
        new_classroom= Classroom(name=name, teacher_id=teacher_id)
        self.db.add(new_classroom)
        self.db.commit()
        self.db.refresh(new_classroom)
        return new_classroom
    def delete(self,classroom_id:UUID)->bool:
        classroom=self.db.query(Classroom).filter(Classroom.id==classroom_id).first()
        if classroom:
            self.db.delete(classroom)  
            self.db.commit()    
            return True 
        return False
    def update(self,classroom_id:UUID,**kwargs)->Optional[Classroom]:
        classroom= self.get_by_id(classroom_id)
        if not classroom:
            return None
        for key, value in kwargs.items():
            if hasattr(classroom, key):
                setattr(classroom, key, value)
            else:
                # Now it will raise the error your test is looking for!
                raise AttributeError(f"Classroom model has no attribute '{key}'")
        self.db.commit()
        self.db.refresh(classroom)   
        return classroom
    
    

    def get_by_id(self,classroom_id:UUID)->Optional[Classroom]:
        return self.db.query(Classroom).filter(Classroom.id==classroom_id).first()
    ## Finding classroom by id, returning a classroom object or None if not found.
    def get_by_teacher_id(self,teacher_id:UUID)->List[Classroom]:
        return self.db.query(Classroom).filter(Classroom.teacher_id==teacher_id).all()
    ## Finding classrooms by teacher_id, returning a list of classroom objects.
    ## If no one was found, it will return an empty list.

    def get_multi(self, skip: int = 0, limit: int = 100):
        # This tells PostgreSQL: "Skip the first X rows, and grab the next Y rows."
        # This is called 'Pagination' and it's crucial so your API doesn't crash 
        # if a school has 10,000 classrooms.
        return self.db.query(Classroom).offset(skip).limit(limit).all()  
    

    def get_classroom_leaderboard(self, classroom_id: UUID, semester: int) -> List[LeaderboardRow]:
        # This is a more complex query that joins the students and their scores to calculate GPA and rank.
        # It uses SQLAlchemy's func.rank() to calculate the rank based on GPA.
        gpa_calc = func.round(
            func.sum(StudentScore.score * AssessmentTemplate.coefficient) / func.sum(AssessmentTemplate.coefficient), 2)
         

        rank_calc = func.rank().over(order_by=gpa_calc.desc())

        leaderboard= (self.db.query(
            Student.id.label("student_id"),
            Student.name.label("student_name"),
            gpa_calc.label("gpa"),
            rank_calc.label("class_rank"),
        ).join(
            StudentScore, Student.id == StudentScore.student_id
        ).join(
            AssessmentTemplate, StudentScore.assessment_template_id == AssessmentTemplate.id
        ).filter(
            Student.classroom_id == classroom_id,
            AssessmentTemplate.semester == semester,
            StudentScore.status == Status.GRADED  # Exclude PENDING scores
        )
        .group_by(Student.id)
        .all()
        )
        formatted_leaderboard = [LeaderboardRow(student_id=row.student_id,
                                                student_name=row.student_name,
                                                gpa=row.gpa,
                                                class_rank=row.class_rank)
                                                for row in leaderboard]
        return formatted_leaderboard

        
    



        
    


    

    