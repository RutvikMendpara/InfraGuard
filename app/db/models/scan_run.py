import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer

from app.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    status = Column(String, default="RUNNING", nullable=False)

    started_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    total_findings = Column(Integer, default=0)