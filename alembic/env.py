import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# ==============================================================================
# 1. THE MAP (Path Setup)
# Alembic usually runs trapped inside its own folder. This line forces it to
# look at the root directory so it can actually find our 'core', 'db', and 'api' folders.
# ==============================================================================
sys.path.append(str(Path(__file__).parent.parent))


# ==============================================================================
# 2. THE MIDFIELDER & THE WALKIE-TALKIE (Config Setup)
# ==============================================================================
config = context.config
from core.config import settings

# The Midfielder: Ignore the fake, hardcoded URL in 'alembic.ini'
# Instead, dynamically grab the real PostgreSQL URL from our .env file.
config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URL))

# The Walkie-Talkie: This reads the formatting rules in 'alembic.ini' and turns on
# the logging system. Without this, Alembic builds the database silently and 
# prints absolutely nothing to the terminal.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ==============================================================================
# 3. THE EYES (Models & Metadata)
# SQLAlchemy's Base.metadata only remembers tables if you explicitly import them.
# If we don't import User, Student, etc. here, Alembic will be "blind", think 
# the database is supposed to be empty, and generate a blank blueprint.
# ==============================================================================
from db.base import Base 
from db.models.user import User
from db.models.classroom import Classroom
from db.models.student import Student
from db.models.subject import Subject
from db.models.assessment_template import AssessmentTemplate
from db.models.student_score import StudentScore

# Hand the "Eyes" over to Alembic so it knows what to build
target_metadata = Base.metadata


# ==============================================================================
# 4. THE REMOTE ARCHITECT (Offline Mode)
# Used when you DON'T have the database password (like enterprise/bank clients).
# It does NOT connect to the database. It just translates Python code into a 
# raw '.sql' text file so you can email it to the client for them to run safely.
# (Run via: alembic upgrade head --sql)
# ==============================================================================
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True, # Magic word: "Write raw SQL text, don't execute it"
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ==============================================================================
# 5. THE LIVE CONSTRUCTION WORKER (Online Mode)
# Used for daily dev/freelancing. This creates a live internet connection to 
# PostgreSQL and physically executes the SQL commands to build/drop tables instantly.
# ==============================================================================
def run_migrations_online() -> None:
    # Build the "Truck" and give it the database URL coordinates
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool, # "Don't park the truck. Drop the tables and leave."
    )

    # Plug the live cable into PostgreSQL
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # The Safety Net: If building table 4 crashes, undo tables 1, 2, and 3 
        # so the database doesn't get permanently corrupted.
        with context.begin_transaction():
            context.run_migrations()


# ==============================================================================
# 6. THE TRAFFIC COP (Execution Logic)
# Checks the terminal command. If you asked for a text file (--sql), it routes 
# to the Architect. Otherwise, it routes to the Live Worker.
# ==============================================================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
