from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from enum import Enum

from app.api.deps import get_db
from app.repositories import finding_repo
from app.schemas.finding import FindingResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


# ---------- ENUMS ----------
class SeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class StatusEnum(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class SortField(str, Enum):
    first_seen_at = "first_seen_at"
    last_seen_at = "last_seen_at"
    severity = "severity"


# ---------- ENDPOINT ----------
@router.get(
    "/",
    response_model=PaginatedResponse[FindingResponse],
    summary="List findings",
    description="Retrieve findings with filters, pagination and sorting",
)
def list_findings(
    severity: SeverityEnum | None = Query(None),
    status: StatusEnum | None = Query(None),
    region: str | None = Query(None),
    resource_type: str | None = Query(None),

    sort_by: SortField = Query(SortField.last_seen_at),
    desc: bool = Query(True, description="Sort descending"),

    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),

    db: Session = Depends(get_db),
):
    filters = {}

    if severity:
        filters["severity"] = severity.value

    if status:
        filters["status"] = status.value

    if region:
        filters["region"] = region

    if resource_type:
        filters["resource_type"] = resource_type

    total, data = finding_repo.get_findings(
        db=db,
        filters=filters,
        limit=limit,
        offset=offset,
        sort_by=sort_by.value,
        desc=desc,
    )

    return PaginatedResponse(
        total=total,
        limit=limit,
        offset=offset,
        data=[FindingResponse.model_validate(f) for f in data],
    )