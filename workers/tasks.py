import logging
from dataclasses import asdict
from uuid import UUID

from core.celery_app import celery_app
from db.session import Sessionlocal  # Import your SQLAlchemy Session Maker
from repositories.grading_repo import GradingRepository  # Update import path as needed

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    name="calculate_classroom_yearly_gpas"
)
def calculate_classroom_yearly_gpas_task(self, classroom_id_str: str) -> dict:
    """
    Background worker task to calculate yearly GPAs for an entire classroom 
    using your GradingRepository.
    """
    logger.info(f"⏳ [CELERY WORKER] Starting Yearly GPA calculation for classroom: {classroom_id_str}")

    # 1. Create a fresh DB session for the worker process
    db = Sessionlocal()

    try:
        # 2. Convert string back to UUID
        classroom_id = UUID(classroom_id_str)

        # 3. Instantiate your GradingRepository
        repo = GradingRepository(db)

        # 4. Call your repository method
        yearly_gpas = repo.get_classroom_yearly_gpas(classroom_id)

        # 5. Convert Dataclass list items into raw Python dicts for JSON serialization
        serialized_data = [asdict(item) for item in yearly_gpas]

        logger.info(f"✅ [CELERY WORKER] Processed {len(serialized_data)} student GPAs successfully.")

        return {
            "status": "SUCCESS",
            "classroom_id": classroom_id_str,
            "processed_count": len(serialized_data),
            "data": serialized_data
        }

    except Exception as exc:
        logger.error(f"❌ [CELERY WORKER FAILED] Error during calculation: {exc}")
        db.rollback()
        raise exc

    finally:
        # 6. Always close database session
        db.close()