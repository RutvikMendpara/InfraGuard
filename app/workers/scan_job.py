from rq import get_current_job

from app.db.session import SessionLocal
from app.repositories import scan_repo
from app.services.scanner_service import run_scan
from app.notifier.notifier import notify
from app.utils import filter_by_severity
from app.core.logger import logger


def run_scan_job(scan_id: str):
    db = SessionLocal()
    job = get_current_job()

    try:
        logger.info(f"Starting scan job: {scan_id}")

        scan = scan_repo.get_scan_by_id(db, scan_id)
        if not scan:
            logger.error("Scan not found")
            return

        scan_repo.start_scan(db, scan)

        findings = run_scan(db)

        notify(filter_by_severity(findings))

        scan_repo.complete_scan(
            db=db,
            scan=scan,
            total_findings=len(findings),
        )

        logger.info(f"Scan completed: {scan_id}")

    except Exception as e:
        logger.error(f"Scan failed: {e}")

        scan = scan_repo.get_scan_by_id(db, scan_id)

        if scan:
            if job and job.retries_left:
                scan_repo.increment_retry(db, scan)
                scan.status = "RETRYING" # type: ignore
            else:
                scan_repo.fail_scan(db, scan)

            db.commit()

        raise  # required for retry

    finally:
        db.close()