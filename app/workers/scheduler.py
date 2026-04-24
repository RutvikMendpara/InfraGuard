import time

from app.core.queue import queue
from app.workers.scan_job import run_scan_job
from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories import scan_repo
from app.core.logger import logger


def start_scheduler():
    if not settings.ENABLE_SCHEDULER:
        logger.info("Scheduler disabled")
        return

    logger.info("Scheduler started")

    while True:
        db = SessionLocal()

        try:
            scan = scan_repo.create_scan(db)

            logger.info(f"Scheduling scan: {scan.id}")

            queue.enqueue(run_scan_job, str(scan.id))

        except Exception as e:
            logger.error(f"Scheduler error: {e}")

        finally:
            db.close()

        time.sleep(settings.SCAN_INTERVAL_SECONDS)