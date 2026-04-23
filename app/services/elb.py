import boto3
from app.config import AWS_CONFIG
from app.utils import make_finding
from app.services.ec2 import check_security_group


def scan(region):
    elbv2 = boto3.client("elbv2", region_name=region, config=AWS_CONFIG)
    ec2 = boto3.client("ec2", region_name=region, config=AWS_CONFIG)

    findings = []
    sg_cache = {}

    def get_sg(sg_id):
        if sg_id not in sg_cache:
            sg_cache[sg_id] = ec2.describe_security_groups(
                GroupIds=[sg_id]
            )["SecurityGroups"][0]
        return sg_cache[sg_id]

    paginator = elbv2.get_paginator("describe_load_balancers")

    for page in paginator.paginate():
        for lb in page["LoadBalancers"]:
            name = lb["LoadBalancerName"]

            has_open_ports = False

            for sg_id in lb.get("SecurityGroups", []):
                sg = get_sg(sg_id)

                sg_findings = check_security_group(sg)

                if sg_findings:
                    has_open_ports = True

                for severity, issue in sg_findings:
                    findings.append(
                        make_finding("ELB", name, region, severity, issue)
                    )

            # Only flag internet-facing if risky
            if lb["Scheme"] == "internet-facing" and has_open_ports:
                findings.append(
                    make_finding("ELB", name, region, "HIGH", "INTERNET_FACING_WITH_OPEN_PORTS")
                )

    return findings