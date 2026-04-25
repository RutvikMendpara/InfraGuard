from rq import Worker
from threading import Thread

from app.core.queue import redis_conn
from app.core.config import settings
from app.core.logger import logger

from app.workers.scheduler import start_scheduler
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.repositories.scan_repo import recover_stuck_scans


def bootstrap():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        logger.info("Recovering stuck scans...")
        recover_stuck_scans(db)

    except Exception as e:
        logger.error(f"Bootstrap error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    bootstrap()

    if settings.ENABLE_SCHEDULER:
        Thread(target=start_scheduler, daemon=True).start()

    worker = Worker([settings.APP_NAME], connection=redis_conn)
    worker.work()