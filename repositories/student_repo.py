from uuid import UUID 
from sqlalchemy import Integer, String, cast, func
from db.models.student import Student
from db.models.grade import Grade
from sqlalchemy.orm import Session  
from db.models.student import Student 
from typing import List, Optional  

from dataclasses import dataclass
from uuid import UUID

# This tells VS Code exactly what the data looks like!
class ReportCardDTO:
    student_id: UUID
    student_name: str
    gpa: float
    rank: int

class StudentRepository: 
    def __init__(self,db: Session):
        self.db=db 

    def create(self,name:str,classroom_id: UUID)->Student:
        new_student=Student(name=name,classroom_id=classroom_id)
        self.db.add(new_student)
        self.db.commit()
        self.db.refresh(new_student)
        return new_student  
    def delete(self,student_id:UUID)->bool:
        student=self.db.query(Student).filter(Student.id==student_id).first()
        if student:
            self.db.delete(student)
            self.db.commit()    
            return True 
        return False 

    def get_by_id(self,student_id:UUID)->Optional[Student]:
        return self.db.query(Student).filter(Student.id== student_id).first()
    ## Finding student by id, returning a student object or None if not found.
    ## we can add more filter conditions just by adding commas in the filter method, for example: filter(Student.id== student_id, Student.name==name) to find by name and id.
    def get_by_classroom_id(self,classroom_id:UUID)->List[Student]:
        return self.db.query(Student).filter(Student.classroom_id==classroom_id).all()
    ## Finding students by classroom_id, returning a list of student objects.
    ## If no one was found, it will return an empty list. 
    def update(self,student_id:UUID,**kwargs)->Optional[Student]:
        student= self.get_by_id(student_id)
        if not student:
            return None
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
            else:
                # Now it will raise the error your test is looking for!
                raise AttributeError(f"Student model has no attribute '{key}'")
        self.db.commit()
        self.db.refresh(student)   
        return student 
    
    def get_multi(self, skip: int = 0, limit: int = 100):
    # This tells PostgreSQL: "Skip the first X rows, and grab the next Y rows."
    # This is called 'Pagination' and it's crucial so your API doesn't crash 
    # if a school has 10,000 classrooms.
        return self.db.query(Student).offset(skip).limit(limit).all()   
    



    def get_student_rank_and_gpa(self, student_id: UUID) -> Optional[ReportCardDTO]:
        student = self.get_by_id(student_id)
        if not student or not student.classroom_id:
            return None    
            
        classroom_id = student.classroom_id 

        # 1. Create the casted variable
        

        # 2. Use numeric_coeff EVERYWHERE instead of Grade.coefficient
        gpa_calc = func.sum(Grade.score * Grade.coefficient) / func.sum(Grade.coefficient)

        rank_calc = func.rank().over(order_by=gpa_calc.desc())

        classroom_stats = (  
            self.db.query(
                Student.id.label('student_id'),
                Student.name.label('student_name'),
                gpa_calc.label('gpa'),
                rank_calc.label('rank')
            )
            .join(Grade, Grade.student_id == Student.id)
            .filter(Student.classroom_id == classroom_id)
            .group_by(Student.id)
            .subquery()
        )
        
        final_result = (
            self.db.query(classroom_stats)
            .filter(classroom_stats.c.student_id == student_id) 
            .first()
        )

        return final_result
# this final result is a row object, which is like our own version of a student object(with extra gpa and rank attributes) 


    


