from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# 1. DATABASE & MODEL IMPORTS
# ==========================================
from db.base import Base
from db.session import engine
# We must import all models here so SQLAlchemy registers them before creating the tables!
from db.models.user import User
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.subject import Subject
from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore 


# ==========================================
# 2. ROUTER IMPORTS
# ==========================================
from api import (
    setup,
    auth, 
    classrooms, 
    students, 
    assessment_templates, 
    student_scores, 
    grading
)

# Initialize database tables (MVP approach)
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. APP INITIALIZATION
# ==========================================
app = FastAPI(
    title="Student Management API",
    description="A professional backend for managing classrooms, students, and GPAs.",
    version="1.0.0"
)

# ==========================================
# 4. CORS CONFIGURATION
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your PyQt5/Web URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 5. ROUTER REGISTRATION
# ==========================================
# Grouped logically so your Swagger UI looks incredibly clean

# System & Auth
app.include_router(setup.router, prefix="/api/setup", tags=["System Setup"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Core Entities
app.include_router(classrooms.router, prefix="/api/classrooms", tags=["Classrooms"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])

# Grading Ecosystem
app.include_router(assessment_templates.router, prefix="/api/assessment-templates", tags=["Assessment Templates"])
app.include_router(student_scores.router, prefix="/api/scores", tags=["Student Scores"])
app.include_router(grading.router, prefix="/api/grading", tags=["Grading & Reports"])

# ==========================================
# 6. ROOT ENDPOINT
# ==========================================
@app.get("/", tags=["Health Check"])
def root():
    """Health check endpoint to ensure the server is alive."""
    return {"message": "API is live! Go to /docs to view the Swagger UI."}

from fastapi import FastAPI
from datetime import datetime

app = FastAPI() # Use your existing FastAPI app instance

@app.get("/health", tags=["System Health"])
def health_check():
    """
    Lightweight endpoint to confirm the API is live, 
    running the correct version, and fully operational.
    """
    return {
        "status": "operational",
        "environment": "production",
        "version": "1.0.1",  # Bump this number whenever you merge new changes
        "timestamp": datetime.utcnow().isoformat()
    }