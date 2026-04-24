import boto3
from app.core.config import settings
from app.utils import make_finding


def get_active_subnets(ec2):
    subnets = set()

    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for res in page["Reservations"]:
            for instance in res["Instances"]:
                subnet_id = instance.get("SubnetId")
                if subnet_id:
                    subnets.add(subnet_id)

    return subnets


def scan(region):
    ec2 = boto3.client("ec2", region_name=region, config=settings.AWS_CONFIG)
    findings = []

    active_subnets = get_active_subnets(ec2)

    paginator = ec2.get_paginator("describe_network_acls")

    for page in paginator.paginate():
        for nacl in page["NetworkAcls"]:
            nacl_id = nacl["NetworkAclId"]

            # ---- Skip unused NACLs ----
            associated = any(
                assoc.get("SubnetId") in active_subnets
                for assoc in nacl.get("Associations", [])
            )

            if not associated:
                continue

            seen = set()  

            for entry in nacl.get("Entries", []):
                if entry.get("RuleAction") != "allow":
                    continue

                if entry.get("CidrBlock") != "0.0.0.0/0":
                    continue

                direction = "INGRESS" if not entry.get("Egress") else "EGRESS"

                port_range = entry.get("PortRange")

                # ---- ALL TRAFFIC ----
                if not port_range:
                    issue = "ALL_PORTS_OPEN"
                    severity = "CRITICAL"

                else:
                    from_port = port_range.get("From")
                    to_port = port_range.get("To")

                    # normalize range
                    if from_port == 0 and to_port == 65535:
                        issue = "ALL_PORTS_OPEN"
                        severity = "CRITICAL"
                    elif from_port in (22, 3389):
                        issue = f"PORT_{from_port}_OPEN"
                        severity = "CRITICAL"
                    else:
                        issue = f"PORT_{from_port}_OPEN"
                        severity = "HIGH"

                key = (direction, issue)

                if key in seen:
                    continue

                seen.add(key)

                findings.append(
                    make_finding(
                        "NACL",
                        nacl_id,
                        region,
                        severity,
                        f"{direction}_{issue}"
                    )
                )

    return findings