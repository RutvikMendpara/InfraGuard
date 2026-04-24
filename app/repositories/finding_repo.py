from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models.finding import Finding


def utc_now():
    return datetime.now(timezone.utc)



def get_by_hash(db: Session, hash_value: str):
    return db.query(Finding).filter(Finding.hash == hash_value).first()


def create_or_update(db: Session, finding_data: dict):
    existing = get_by_hash(db, finding_data["hash"])

    if existing:
        existing.last_seen_at = utc_now() # type: ignore
        existing.status = "OPEN" # type: ignore
        db.commit()
        return existing

    new_finding = Finding(**finding_data)
    db.add(new_finding)
    db.commit()
    db.refresh(new_finding)
    return new_finding


def mark_missing_as_resolved(db: Session, active_hashes: set):
    findings = db.query(Finding).filter(Finding.status == "OPEN").all()

    for f in findings:
        if f.hash not in active_hashes:
            f.status = "RESOLVED" # type: ignore

    db.commit()


def get_findings(db, filters, limit, offset, sort_by="last_seen_at", desc=True):
    query = db.query(Finding)

    if "severity" in filters:
        query = query.filter(Finding.severity == filters["severity"])

    if "status" in filters:
        query = query.filter(Finding.status == filters["status"])

    if "region" in filters:
        query = query.filter(Finding.region == filters["region"])

    if "resource_type" in filters:
        query = query.filter(Finding.resource_type == filters["resource_type"])

    total = query.count()

    sort_column = getattr(Finding, sort_by)

    if desc:
        sort_column = sort_column.desc()

    query = query.order_by(sort_column)

    data = query.offset(offset).limit(limit).all()

    return total, data