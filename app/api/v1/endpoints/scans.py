from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories import scan_repo
from app.services.scanner_service import run_scan
from app.schemas.scan import ScanResponse
from app.notifier.notifier import notify
from app.utils import filter_by_severity
router = APIRouter()


@router.post(
    "/",
    response_model=ScanResponse,
    summary="Trigger scan",
    description="Run full AWS infra scan and persist findings",
)
def trigger_scan(db: Session = Depends(get_db)):
    scan = scan_repo.create_scan(db)

    try:
        findings = run_scan(db)

        alert_findings = filter_by_severity(findings)
        notify(alert_findings)

        scan = scan_repo.complete_scan(
            db=db,
            scan=scan,
            total_findings=len(findings),
        )

        return scan

    except Exception as e:
        scan.status = "FAILED"  # type: ignore
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/",
    response_model=list[ScanResponse],
    summary="List scan runs",
    description="Fetch history of scan executions",
)
def list_scans(db: Session = Depends(get_db)):
    return scan_repo.get_scans(db)