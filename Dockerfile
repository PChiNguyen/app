# 1. Pull the official, lightweight Python engine
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements first (makes rebuilding incredibly fast)
COPY requirements.txt .

# 4. Install all your Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your actual code into the container
COPY . .

# 6. Expose the port that FastAPI uses
EXPOSE 8000

# 7. Run Celery worker in the background (&) and start Uvicorn in the foreground
CMD ["sh", "-c", "celery -A core.celery_app worker --loglevel=info & uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]