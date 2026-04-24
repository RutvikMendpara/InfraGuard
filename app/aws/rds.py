import boto3
from app.core.config import settings
from app.utils import make_finding
from app.aws.ec2 import check_security_group


def scan(region):
    rds = boto3.client("rds", region_name=region, config=settings.AWS_CONFIG)
    ec2 = boto3.client("ec2", region_name=region, config=settings.AWS_CONFIG)

    findings = []
    sg_cache = {}

    def get_sg(sg_id):
        if sg_id not in sg_cache:
            sg_cache[sg_id] = ec2.describe_security_groups(
                GroupIds=[sg_id]
            )["SecurityGroups"][0]
        return sg_cache[sg_id]

    paginator = rds.get_paginator("describe_db_instances")

    for page in paginator.paginate():
        for db in page["DBInstances"]:
            db_id = db["DBInstanceIdentifier"]

            if db.get("PubliclyAccessible"):
                findings.append(
                    make_finding("RDS", db_id, region, "CRITICAL", "PUBLIC_DB")
                )

            if not db.get("StorageEncrypted"):
                findings.append(
                    make_finding("RDS", db_id, region, "HIGH", "NO_ENCRYPTION")
                )

            if db.get("BackupRetentionPeriod", 0) == 0:
                findings.append(
                    make_finding("RDS", db_id, region, "MEDIUM", "BACKUP_DISABLED")
                )

            for sg in db.get("VpcSecurityGroups", []):
                sg_data = get_sg(sg["VpcSecurityGroupId"])

                for severity, issue in check_security_group(sg_data):
                    findings.append(
                        make_finding("RDS", db_id, region, severity, issue)
                    )

    return findings