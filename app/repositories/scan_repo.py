from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models.scan_run import ScanRun


def utc_now():
    return datetime.now(timezone.utc)


def create_scan(db: Session):
    scan = ScanRun()
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def complete_scan(db: Session, scan: ScanRun, total_findings: int):
    scan.status = "SUCCESS" # type: ignore
    scan.completed_at = utc_now() # type: ignore
    scan.total_findings = total_findings # type: ignore
    db.commit()
    return scan


def get_scans(db: Session):
    return db.query(ScanRun).order_by(ScanRun.started_at.desc()).all()