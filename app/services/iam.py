import boto3
import json
from app.config import AWS_CONFIG
from app.utils import make_finding

iam = boto3.client("iam", config=AWS_CONFIG)


def has_admin_policy(policy_doc):
    for stmt in policy_doc.get("Statement", []):
        if stmt.get("Effect") != "Allow":
            continue

        actions = stmt.get("Action")
        resources = stmt.get("Resource")

        if actions == "*" or actions == ["*"]:
            return True

        if isinstance(actions, list) and "*" in actions:
            return True

        if resources == "*" or resources == ["*"]:
            return True

    return False


def scan():
    findings = []

    # users
    paginator = iam.get_paginator("list_users")

    for page in paginator.paginate():
        for user in page["Users"]:
            username = user["UserName"]

            # MFA 
            mfa = iam.list_mfa_devices(UserName=username)
            if not mfa.get("MFADevices"):
                findings.append(
                    make_finding("IAM", username, "global", "HIGH", "MFA_NOT_ENABLED")
                )

            attached = iam.list_attached_user_policies(UserName=username)
            for pol in attached.get("AttachedPolicies", []):
                if pol["PolicyName"] == "AdministratorAccess":
                    findings.append(
                        make_finding("IAM", username, "global", "CRITICAL", "ADMIN_ACCESS")
                    )

    # roles
    paginator = iam.get_paginator("list_roles")

    for page in paginator.paginate():
        for role in page["Roles"]:
            role_name = role["RoleName"]

            attached = iam.list_attached_role_policies(RoleName=role_name)

            for pol in attached.get("AttachedPolicies", []):
                if pol["PolicyName"] == "AdministratorAccess":
                    findings.append(
                        make_finding("IAM", role_name, "global", "CRITICAL", "ADMIN_ROLE")
                    )

    return findings