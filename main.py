from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Import your routers
from api import auth, classrooms, students

from db.base import Base # Or wherever your Base is located
from db.session import engine # Import the engine you just updated
from db.models.user import User
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.subject import  Subject
from db.models.assessment_template import  AssessmentTemplate
from db.models.student_score import StudentScore 


# This tells SQLAlchemy to look at all your models and build the SQLite file!
Base.metadata.create_all(bind=engine)


# from api import students  <-- You will uncomment this when we build it

app = FastAPI(
    title="Student Management API",
    description="A professional backend for managing classrooms, students, and GPAs.",
    version="1.0.0"
)

# ==========================================
# CORS (Cross-Origin Resource Sharing)
# ==========================================
# This is crucial for when you hook up your PyQt5 app or a web frontend.
# It tells your API "Yes, it is safe to talk to these specific external apps."
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change "*" to your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTER REGISTRATION
# ==========================================
# We use 'prefix' so you don't have to type '/api/classrooms' inside the classrooms.py file.
# We use 'tags' so your Swagger UI groups them into beautiful, organized sections.

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(classrooms.router, prefix="/api/classrooms", tags=["Classrooms"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])




# app.include_router(students.router, prefix="/api/students", tags=["Students"])

@app.get("/")
def root():
    """Health check endpoint to make sure the server is alive."""
    return {"message": "API is live! Go to /docs to view the Swagger UI."}