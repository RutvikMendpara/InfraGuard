import boto3
from .ec2 import check_security_group


def scan(region):
    elbv2 = boto3.client("elbv2", region_name=region)
    ec2 = boto3.client("ec2", region_name=region)

    results = []

    lbs = elbv2.describe_load_balancers()["LoadBalancers"]

    for lb in lbs:
        name = lb["LoadBalancerName"]
        findings = []

        if lb["Scheme"] == "internet-facing":
            findings.append(("HIGH", "INTERNET_FACING"))

        for sg_id in lb.get("SecurityGroups", []):
            sg = ec2.describe_security_groups(GroupIds=[sg_id])["SecurityGroups"][0]
            findings.extend(check_security_group(sg))

        results.append((name, findings))

    return results