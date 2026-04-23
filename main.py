from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from app.services import ec2, s3, nacl, elb
from app.utils import get_all_regions, filter_by_severity, print_summary
from app.notifier import notify
from app import settings
from app.logger import logger


def run_scan():
    all_findings = []

    logger.info("Starting S3 scan")
    s3_findings = s3.scan()
    logger.info(f"S3 findings: {len(s3_findings)}")
    all_findings.extend(s3_findings)

    regions = get_all_regions()
    logger.info(f"Scanning regions: {regions}")

    with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
        futures = {
            executor.submit(scan_region, region): region
            for region in regions
        }

        for future in as_completed(futures):
            region = futures[future]
            try:
                region_findings = future.result()
                logger.info(f"{region}: {len(region_findings)} findings")
                all_findings.extend(region_findings)
            except Exception as e:
                logger.error(f"{region} failed: {e}")

    return all_findings


def scan_region(region):
    logger.info(f"Scanning region: {region}")

    findings = []
    findings.extend(ec2.scan(region))
    findings.extend(nacl.scan(region))
    findings.extend(elb.scan(region))

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