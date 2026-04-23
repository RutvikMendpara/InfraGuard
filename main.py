from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from app.services import ec2, s3, nacl, elb, iam, rds, cloudtrail
from app.utils import get_all_regions, filter_by_severity, print_summary
from app.notifier import notify
from app import settings
from app.logger import logger


def run_scan():
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

    return all_findings


def scan_region(region):
    logger.info(f"Scanning region: {region}")

    findings = []
    findings.extend(ec2.scan(region))
    findings.extend(nacl.scan(region))
    findings.extend(elb.scan(region))
    findings.extend(rds.scan(region))
    return findings


def main():
    logger.info("InfraGuard started")

    while True:
        start_time = time.time()

        findings = run_scan()

        logger.info(f"Total findings: {len(findings)}")

        print_summary(findings)

        alert_findings = filter_by_severity(findings)
        logger.info(f"Alert-worthy findings: {len(alert_findings)}")

        notify(alert_findings)

        duration = round(time.time() - start_time, 2)
        logger.info(f"Scan completed in {duration}s")

        logger.info(f"Sleeping for {settings.SCAN_INTERVAL_SECONDS} seconds\n")

        time.sleep(settings.SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()