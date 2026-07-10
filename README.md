Markdown
# 🎓 Nguyễn Võ Thảo Nguyên ơi tui thích bà

A professional, high-performance RESTful API designed to manage classrooms, students, and complex grading systems. Built with modern Python backend architecture.

## 🚀 Tech Stack
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Authentication:** JWT (JSON Web Tokens)
* **Testing:** Pytest

## ✨ Key Features
* **Role-Based Access Control (RBAC):** Secure endpoints with strict permissions for Teachers, Admins, and Students.
* **Complex Grading Engine:** Automated calculation of Subject Averages, Semester GPAs, and Yearly GPAs using optimized SQL aggregations.
* **Bulletproof Testing:** Comprehensive Pytest suite covering happy paths, sad paths, and edge cases to ensure data integrity.
* **Auto-Generated Docs:** Built-in Swagger UI integration for seamless API testing.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/PChiNguyen/app.git](https://github.com/PChiNguyen/app.git)
   cd app
Create a virtual environment:

Bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Environment Setup:
Create a .env file in the root directory and add your configuration keys:

Ini, TOML
PROJECT_NAME="Nguyễn Võ Thảo Nguyên ơi tui thích bà"
SECRET_KEY="Nguyen_Vo_Thao_Nguyen_i_like_u"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080
SQLALCHEMY_DATABASE_URL="postgresql://postgres:<your_password>@localhost:5432/school_db"
Run the server:

Bash
uvicorn main:app --reload
📖 API Documentation
Once the server is running, navigate to http://127.0.0.1:8000/docs to view the interactive Swagger UI documentation and test the endpoints directly.

🐳 Future Roadmap
Containerizing the application using Docker for cross-platform deployment.

Developing a dedicated frontend UI dashboard using PyQt5.

👨‍💻 Author
Nguyenlaze

GitHub: @PChiNguyen