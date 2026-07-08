# ============================================================================
# 🚀 LOCAL SERVER
# ============================================================================
# Start the FastAPI server with live reloading
run:
	python -m uvicorn main:app --reload

# ============================================================================
# 📦 ENVIRONMENT & SETUP
# ============================================================================
# 1. Create the virtual environment (Run this ONCE when setting up the project)
init:
	python -m venv .venv
	@echo "⚠️ Virtual environment created!"
	@echo "👉 Now you MUST run this in your terminal: .venv\Scripts\activate"

# 2. Install all required libraries
install:
	pip install -r requirements.txt

# 3. Save your current installed libraries to the list
req:
	pip freeze > requirements.txt

# ============================================================================
# 🗄️ DATABASE (ALEMBIC)
# ============================================================================
# Auto-generate a new database migration file after changing a model
db-make:
	alembic revision --autogenerate -m "auto_update"

# Push the migration to the PostgreSQL database
db-push:
	alembic upgrade head

# ============================================================================
# 🧪 TESTING
# ============================================================================
# Run all Pytest tests normally
test:
	pytest -v

# Run tests continuously while you code, and show a coverage report
auto-watch:
	ptw -- --cov=. --cov-report=term-missing --cov-report=xml

# ============================================================================
# 🧹 UTILITIES
# ============================================================================
# Clean up junk cache files that Python leaves behind
clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"


## installing unicorn in my env: pip install "uvicorn[standard]" fpdf2


# ==========================================
# THPT AN PHUOC - DOCKER SHORTCUTS
# ==========================================

# 1. Start the project
# What it does: Turns on your API, Database, and pgAdmin in the background.
# When to use: When you sit down to start coding for the day.
up:
	docker-compose up -d

# 2. Stop the project
# What it does: Safely shuts down all containers.
# When to use: When you are done working.
down:
	docker-compose down

# 3. Rebuild the project
# What it does: Re-installs everything from scratch. 
# When to use: Use this ONLY when you add new things to requirements.txt or change the Dockerfile.
build:
	docker-compose up -d --build

# 4. Build/Update the Database Tables
# What it does: Runs Alembic to create your tables in Postgres.
# When to use: After you create or change a class in models.py.
migrate:
	docker-compose exec api alembic upgrade head

# 5. Create your test user
# What it does: Runs your create_user.py script.
# When to use: When you need to inject your testing teacher into a fresh database.
create-user:
	docker-compose exec api python create_user.py
create-subject:
	docker-compose exec api python create_subject.py  


logs-api:
	docker-compose logs -f api

# Watch the Database logs in real-time
logs-db:
	docker-compose logs -f db

# See just the last 100 lines of everything if you get a random error
logs-all:
	docker-compose logs --tail 100


# ==========================================
# ADVANCED DEBUGGING
# ==========================================

# Use this ONLY if Alembic throws an "Already Exists" error.
# It forces Alembic to pretend it successfully ran the latest migration.
stamp:
	docker-compose exec api alembic stamp head 