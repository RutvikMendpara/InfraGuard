import time

from app.core.logger import logger
from app.core.config import settings

from app.db.session import SessionLocal
from app.services.scanner_service import run_scan
from app.notifier.notifier import notify
from app.utils import filter_by_severity


def start_worker():
    logger.info("Scan worker started")

    while True:
        db = SessionLocal()

        try:
            findings = run_scan(db)

            alert_findings = filter_by_severity(findings)

            notify(alert_findings)

        except Exception as e:
            logger.error(f"Worker error: {e}")

        finally:
            db.close()

        logger.info(f"Sleeping for {settings.SCAN_INTERVAL_SECONDS} seconds")
        time.sleep(settings.SCAN_INTERVAL_SECONDS)