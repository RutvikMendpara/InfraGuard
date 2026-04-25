import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Index, UniqueConstraint

from app.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    region = Column(String, nullable=False)

    severity = Column(String, nullable=False)
    issue = Column(String, nullable=False)

    status = Column(String, default="OPEN", nullable=False)

    hash = Column(String, nullable=False, index=True)

    first_seen_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    last_seen_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    __table_args__ = (
         UniqueConstraint("hash", name="uq_finding_hash"),
    )