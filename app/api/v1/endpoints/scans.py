from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.queue import queue
from app.workers.scan_job import run_scan_job
from app.api.deps import get_db
from app.repositories import scan_repo
from app.services.scanner_service import run_scan
from app.schemas.scan import ScanResponse
from app.notifier.notifier import notify
from app.utils import filter_by_severity
from rq import Retry

router = APIRouter()


@router.post(
    "/",
    response_model=ScanResponse,
    summary="Trigger scan",
    description="Enqueue AWS infra scan and return immediately",
)
def trigger_scan(db: Session = Depends(get_db)):
    scan_repo.cleanup_stale_scans(db)

    if scan_repo.has_active_scan(db):
        raise HTTPException(409, "A scan is already running")

    scan = scan_repo.create_scan(db)

    queue.enqueue(
        run_scan_job,
        str(scan.id),
        retry=Retry(max=3, interval=[30, 60, 120])
    )

    return scan
    

@router.get(
    "/",
    response_model=list[ScanResponse],
    summary="List scan runs",
)
def list_scans(db: Session = Depends(get_db)):
    return scan_repo.get_scans(db)


@router.get(
    "/{scan_id}",
    response_model=ScanResponse,
    summary="Get scan status",
)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = scan_repo.get_scan_by_id(db, scan_id)

    if not scan:
        raise HTTPException(404, "Scan not found")

    return scan