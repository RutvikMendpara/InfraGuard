import boto3
import json
from botocore.exceptions import ClientError
from app.core.config import settings
from app.utils import make_finding

def get_client():
    return boto3.client("s3", config=settings.AWS_CONFIG)


def is_acl_public(acl):
    for grant in acl.get("Grants", []):
        uri = grant.get("Grantee", {}).get("URI", "")
        if "AllUsers" in uri or "AuthenticatedUsers" in uri:
            return True
    return False


def is_policy_public(policy_json):
    for stmt in policy_json.get("Statement", []):
        if stmt.get("Effect") != "Allow":
            continue

        principal = stmt.get("Principal")

        # Case 1: "*"
        if principal == "*":
            return True

        # Case 2: {"AWS": "*"}
        if isinstance(principal, dict):
            if principal.get("AWS") == "*":
                return True

    return False


def get_public_access_block(bucket):
    s3 = get_client()
    
    try:
        block = s3.get_public_access_block(Bucket=bucket)
        config = block["PublicAccessBlockConfiguration"]
        return config
    except ClientError:
        return None


def scan():
    s3 = get_client()
    findings = []

    buckets = s3.list_buckets().get("Buckets", [])

    for b in buckets:
        name = b["Name"]

        acl_public = False
        policy_public = False
        pab_config = None

        # ---- ACL CHECK ----
        try:
            acl = s3.get_bucket_acl(Bucket=name)
            acl_public = is_acl_public(acl)

            if acl_public:
                findings.append(
                    make_finding("S3", name, "global", "CRITICAL", "ACL_PUBLIC")
                )
        except ClientError:
            pass

        # ---- POLICY CHECK ----
        try:
            policy = s3.get_bucket_policy(Bucket=name)
            policy_json = json.loads(policy["Policy"])

            policy_public = is_policy_public(policy_json)

            if policy_public:
                findings.append(
                    make_finding("S3", name, "global", "CRITICAL", "POLICY_PUBLIC")
                )
        except ClientError:
            pass

        # ---- PUBLIC ACCESS BLOCK CHECK ----
        pab_config = get_public_access_block(name)

        if pab_config is None:
            findings.append(
                make_finding(
                    "S3",
                    name,
                    "global",
                    "HIGH",
                    "PUBLIC_ACCESS_BLOCK_NOT_SET"
                )
            )
        else:
            if not all(pab_config.values()):
                findings.append(
                    make_finding(
                        "S3",
                        name,
                        "global",
                        "HIGH",
                        "PUBLIC_ACCESS_BLOCK_DISABLED"
                    )
                )

        # ---- EFFECTIVE PUBLIC  ----
        if (acl_public or policy_public):
            if pab_config and all(pab_config.values()):
                findings.append(
                    make_finding(
                        "S3",
                        name,
                        "global",
                        "MEDIUM",
                        "PUBLIC_ACCESS_BLOCK_OVERRIDES_PUBLIC_CONFIG"
                    )
                )
            else:
                findings.append(
                    make_finding(
                        "S3",
                        name,
                        "global",
                        "CRITICAL",
                        "BUCKET_EFFECTIVELY_PUBLIC"
                    )
                )

    return findings