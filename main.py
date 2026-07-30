import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone 
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse  
from fastapi import APIRouter
import os 
from core.exceptions import AppException

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# ==========================================
# 3. APP INITIALIZATION (ONLY ONCE!)
# ==========================================
app = FastAPI(
    title="Student Management API",
    description="A professional backend for managing classrooms, students, and GPAs.",
    version="1.0.0"
)
ALLOWED_PRODUCTION_ORIGINS = [
    "https://anphuoc-school.com",          # Your future web frontend
    "https://admin-dashboard.netlify.app", # Your admin panel web deployment
    "http://localhost:3000",               # Local frontend development environment
]
# ==========================================
# 4. CORS CONFIGURATION  
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_PRODUCTION_ORIGINS,
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
# 6. SYSTEM ENDPOINTS
# ==========================================
@app.get("/", tags=["Health Check"])
def root():
    """Health check endpoint to ensure the server is alive."""
    return {"message": "API is live! Go to /docs to view the Swagger UI."}

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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }     

# ==========================================
# EXTRA: SWAGGER 500 ERROR INVESTIGATOR
# ==========================================
@app.exception_handler(Exception)
async def global_crash_catcher(request: Request, exc: Exception):
    """
    Catches any runtime crash, extracts the exact line number, 
    and sends the full traceback report straight to your Swagger UI screen.
    """
    # Convert the scary system crash report into clean, readable text lines
    full_traceback = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    
    # 1. Print it to Render's terminal stream just in case
    print(f"\n[CRASH REPORT] 500 Error on {request.method} {request.url.path}")
    print(full_traceback)
    
    # 2. Package it nicely and send it directly back to your browser screen!
    return JSONResponse(
        status_code=500,
        content={
            "status": "fail",
            "error_class": type(exc).__name__,
            "reason": str(exc),
            "endpoint": request.url.path,
            "fix_instruction": "Look at the traceback array below to find the exact file and line number that failed.",
            "traceback": full_traceback.split("\n")  # Splits text into a clean readable list
        }
    )

@app.get("/api/auth/debug-env-vars", tags=["System Health"])
def debug_environment_variables():
    """
    Safely inspects if Render has injected the REDIS_URL 
    variable into our live app environment.
    """
    raw_redis_url = os.getenv("REDIS_URL")
    
    if not raw_redis_url:
        return {
            "REDIS_URL_STATUS": "❌ NOT FOUND! Your app is blind to it.",
            "current_fallback_being_used": "redis://redis:6379",
            "action_item": "Go to Render Dashboard -> Environment -> Add REDIS_URL"
        }
        
    # Safely mask the password so your secrets stay private
    # Example: redis://:password@host -> redis://:****@host
    masked_url = raw_redis_url
    if "@" in raw_redis_url:
        try:
            prefix, credentials_host = raw_redis_url.split("://")
            credentials, host = credentials_host.split("@")
            masked_url = f"{prefix}://:****@{host}"
        except Exception:
            masked_url = "redis://[Masked Connection String]"

    return {
        "REDIS_URL_STATUS": "✅ FOUND!",
        "detected_value": masked_url,
        "is_using_fallback": False
    }
# ==========================================
# CUSTOM BUSINESS EXCEPTION HANDLER
# ==========================================
@app.exception_handler(AppException)
async def custom_app_exception_handler(request: Request, exc: AppException):
    """
    Catches clean business logic errors (400 Bad Request, 404 Not Found, 409 Conflict)
    and returns a structured JSON message without triggering a 500 server crash report.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "fail",
            "error": exc.message,
            "details": exc.payload
        }
    )