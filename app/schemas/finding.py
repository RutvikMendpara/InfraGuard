from pydantic import BaseModel
from datetime import datetime


class FindingBase(BaseModel):
    resource_type: str
    resource_id: str
    region: str
    severity: str
    issue: str
    status: str


class FindingResponse(FindingBase):
    id: str
    first_seen_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True