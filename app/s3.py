import boto3
import json
from botocore.exceptions import ClientError

s3 = boto3.client("s3")


def is_acl_public(bucket):
    try:
        acl = s3.get_bucket_acl(Bucket=bucket)
        for grant in acl["Grants"]:
            uri = grant.get("Grantee", {}).get("URI", "")
            if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                return True
    except ClientError:
        pass
    return False


def is_policy_public(bucket):
    try:
        policy = s3.get_bucket_policy(Bucket=bucket)
        policy_json = json.loads(policy["Policy"])

        for stmt in policy_json.get("Statement", []):
            if stmt.get("Effect") == "Allow" and stmt.get("Principal") == "*":
                return True
    except ClientError:
        pass
    return False


def is_public_block_disabled(bucket):
    try:
        block = s3.get_public_access_block(Bucket=bucket)
        return not all(block["PublicAccessBlockConfiguration"].values())
    except ClientError:
        return True


def check_encryption(bucket):
    try:
        s3.get_bucket_encryption(Bucket=bucket)
        return True
    except ClientError:
        return False


def check_versioning(bucket):
    try:
        v = s3.get_bucket_versioning(Bucket=bucket)
        return v.get("Status") == "Enabled"
    except ClientError:
        return False


def check_logging(bucket):
    try:
        log = s3.get_bucket_logging(Bucket=bucket)
        return "LoggingEnabled" in log
    except ClientError:
        return False


def scan():
    results = []

    buckets = s3.list_buckets()["Buckets"]

    for b in buckets:
        name = b["Name"]
        findings = []

        if is_acl_public(name):
            findings.append(("CRITICAL", "ACL_PUBLIC"))

        if is_policy_public(name):
            findings.append(("CRITICAL", "POLICY_PUBLIC"))

        if is_public_block_disabled(name):
            findings.append(("HIGH", "PUBLIC_ACCESS_BLOCK_DISABLED"))

        if not check_encryption(name):
            findings.append(("HIGH", "NO_ENCRYPTION"))

        if not check_versioning(name):
            findings.append(("MEDIUM", "VERSIONING_DISABLED"))

        if not check_logging(name):
            findings.append(("MEDIUM", "LOGGING_DISABLED"))

        results.append((name, findings))

    return results