from concurrent.futures import ThreadPoolExecutor, as_completed

from app.aws import ec2, s3, nacl, elb, iam, rds, cloudtrail
from app.core.config import settings
from app.core.logger import logger
from app.utils import get_all_regions

from app.repositories import finding_repo


def generate_hash(f):
    return f"{f['resource_type']}:{f['resource_id']}:{f['region']}:{f['issue']}"


def scan_region(region):
    logger.info(f"Scanning region: {region}")

    findings = []
    findings.extend(ec2.scan(region))
    findings.extend(nacl.scan(region))
    findings.extend(elb.scan(region))
    findings.extend(rds.scan(region))

    return findings


def run_scan(db):
    all_findings = []

    logger.info("Scanning S3")
    all_findings.extend(s3.scan())

    logger.info("Scanning IAM")
    all_findings.extend(iam.scan())

    logger.info("Scanning CloudTrail")
    all_findings.extend(cloudtrail.scan())

    regions = get_all_regions()

    with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
        futures = {
            executor.submit(scan_region, region): region
            for region in regions
        }

        for future in as_completed(futures):
            try:
                all_findings.extend(future.result())
            except Exception as e:
                logger.error(f"Region failed: {e}")

    # --------------------------
    # DB INTEGRATION (CRITICAL)
    # --------------------------

    active_hashes = set()

    for f in all_findings:
        f["hash"] = generate_hash(f)
        active_hashes.add(f["hash"])

        finding_repo.create_or_update(db, f)

    # mark missing findings as resolved
    finding_repo.mark_missing_as_resolved(db, active_hashes)

    return all_findings