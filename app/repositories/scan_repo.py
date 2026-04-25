from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.db.models.scan_run import ScanRun


def utc_now():
    return datetime.now(timezone.utc)


def create_scan(db: Session):
    scan = ScanRun(status="PENDING", started_at=utc_now())
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def start_scan(db: Session, scan: ScanRun):
    scan.status = "RUNNING" # type: ignore
    scan.started_at = utc_now() # type: ignore
    db.commit()


def complete_scan(db: Session, scan: ScanRun, total_findings: int):
    scan.status = "SUCCESS" # type: ignore
    scan.completed_at = utc_now() # type: ignore
    scan.total_findings = total_findings # type: ignore
    db.commit()
    return scan


def fail_scan(db: Session, scan: ScanRun):
    scan.status = "FAILED" # type: ignore
    db.commit()


def increment_retry(db: Session, scan: ScanRun):
    scan.retry_count += 1 # type: ignore
    db.commit()


def get_scans(db: Session):
    return db.query(ScanRun).order_by(ScanRun.started_at.desc()).all()


def get_scan_by_id(db: Session, scan_id: str):
    return db.query(ScanRun).filter(ScanRun.id == scan_id).first()


def has_active_scan(db: Session):
    threshold = utc_now() - timedelta(minutes=30)

    return db.query(ScanRun).filter(
        ScanRun.status.in_(["PENDING", "RUNNING"]),
        ScanRun.started_at >= threshold
    ).first() is not None


def cleanup_stale_scans(db: Session):
    threshold = utc_now() - timedelta(minutes=30)

    db.query(ScanRun).filter(
        ScanRun.status.in_(["PENDING", "RUNNING"]),
        ScanRun.started_at < threshold
    ).update(
        {"status": "FAILED"},
        synchronize_session=False
    )

    db.commit()


def recover_stuck_scans(db: Session):
    db.query(ScanRun).filter(
        ScanRun.status == "RUNNING"
    ).update(
        {"status": "FAILED"},
        synchronize_session=False
    )
    db.commit()