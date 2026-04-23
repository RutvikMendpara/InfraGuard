import boto3
from app.config import AWS_CONFIG
from app import settings


def get_all_regions():
    ec2 = boto3.client("ec2", config=AWS_CONFIG)
    regions = ec2.describe_regions()["Regions"]
    return [r["RegionName"] for r in regions]


def make_finding(resource, resource_id, region, severity, issue):
    return {
        "resource": resource,
        "id": resource_id,
        "region": region,
        "severity": severity,
        "issue": issue,
    }


def filter_by_severity(findings):
    return [
        f for f in findings
        if f["severity"] in settings.ALERT_SEVERITIES
    ]


def summarize_findings(findings):
    summary = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    for f in findings:
        sev = f["severity"]
        if sev in summary:
            summary[sev] += 1

    return summary


def print_summary(findings):
    summary = summarize_findings(findings)

    print("\n=== SUMMARY ===")
    for severity, count in summary.items():
        print(f"{severity}: {count}")