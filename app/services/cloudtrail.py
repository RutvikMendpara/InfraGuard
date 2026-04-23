import boto3
from app.config import AWS_CONFIG
from app.utils import make_finding

ct = boto3.client("cloudtrail", config=AWS_CONFIG)


def scan():
    findings = []

    trails = ct.describe_trails().get("trailList", [])

    if not trails:
        findings.append(
            make_finding("CloudTrail", "account", "global", "CRITICAL", "DISABLED")
        )
        return findings

    for trail in trails:
        name = trail.get("Name")

        if not trail.get("IsMultiRegionTrail"):
            findings.append(
                make_finding("CloudTrail", name, "global", "HIGH", "NOT_MULTI_REGION")
            )

        if not trail.get("LogFileValidationEnabled"):
            findings.append(
                make_finding("CloudTrail", name, "global", "MEDIUM", "LOG_VALIDATION_DISABLED")
            )

    return findings