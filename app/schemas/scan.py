from pydantic import BaseModel
from datetime import datetime


class ScanResponse(BaseModel):
    id: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    total_findings: int

    class Config:
        from_attributes = True