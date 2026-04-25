from app.db.session import SessionLocal
from app.services.scanner_service import run_scan
from app.repositories import scan_repo
from app.notifier.notifier import notify
from app.utils import filter_by_severity
from app.core.logger import logger


def run_scan_job(scan_id: str):
    db = SessionLocal()

    try:
        logger.info(f"Starting async scan job: {scan_id}")

        scan = scan_repo.get_scan_by_id(db, scan_id)
        scan.status = "RUNNING" # type: ignore
        db.commit()
        
        findings = run_scan(db)

        alert_findings = filter_by_severity(findings)
        notify(alert_findings)

        scan_repo.complete_scan(
            db=db,
            scan=scan, # type: ignore
            total_findings=len(findings),
        )

        logger.info(f"Scan completed: {scan_id}")

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        scan = scan_repo.get_scan_by_id(db, scan_id)
        scan.status = "FAILED" # type: ignore
        db.commit()

    finally:
        db.close()