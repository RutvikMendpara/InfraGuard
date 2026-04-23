import boto3
from app.config import AWS_CONFIG
from app.utils import make_finding


def get_all_instances(ec2):
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for res in page["Reservations"]:
            for instance in res["Instances"]:
                yield instance


def check_security_group(sg):
    findings = []

    for perm in sg.get("IpPermissions", []):
        from_port = perm.get("FromPort")

        # ALL TRAFFIC
        if from_port is None:
            findings.append(("CRITICAL", "ALL_PORTS_OPEN"))

        # IPv4
        for ip_range in perm.get("IpRanges", []):
            if ip_range.get("CidrIp") == "0.0.0.0/0":
                if from_port == 22:
                    findings.append(("CRITICAL", "SSH_OPEN"))
                elif from_port == 3389:
                    findings.append(("CRITICAL", "RDP_OPEN"))
                else:
                    findings.append(("HIGH", f"PORT_{from_port}_OPEN"))

        # IPv6
        for ipv6 in perm.get("Ipv6Ranges", []):
            if ipv6.get("CidrIpv6") == "::/0":
                findings.append(("CRITICAL", "IPV6_OPEN"))

    return findings


def scan(region):
    ec2 = boto3.client("ec2", region_name=region, config=AWS_CONFIG)

    findings = []
    sg_cache = {}

    def get_sg(sg_id):
        if sg_id not in sg_cache:
            sg_cache[sg_id] = ec2.describe_security_groups(
                GroupIds=[sg_id]
            )["SecurityGroups"][0]
        return sg_cache[sg_id]

    for instance in get_all_instances(ec2):
        state = instance["State"]["Name"]
        if state != "running":
            continue

        instance_id = instance["InstanceId"]
        public_ip = instance.get("PublicIpAddress")

        seen = set()

        for sg in instance.get("SecurityGroups", []):
            sg_data = get_sg(sg["GroupId"])
            sg_findings = check_security_group(sg_data)

            for severity, issue in sg_findings:
                key = (instance_id, issue)
                if key in seen:
                    continue
                seen.add(key)

                findings.append(
                    make_finding("EC2", instance_id, region, severity, issue)
                )

            if public_ip and sg_findings:
                findings.append(
                    make_finding(
                        "EC2",
                        instance_id,
                        region,
                        "CRITICAL",
                        "PUBLIC_INSTANCE_WITH_OPEN_PORTS"
                    )
                )

    return findings