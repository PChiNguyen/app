from uuid import UUID 
from sqlalchemy.orm import Session  
from db.models.student import Student 
from typing import List, Optional  

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
    


