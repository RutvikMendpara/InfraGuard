import boto3


def get_active_subnets(ec2):
    subnets_with_instances = set()

    reservations = ec2.describe_instances()["Reservations"]
    for res in reservations:
        for instance in res["Instances"]:
            subnet_id = instance.get("SubnetId")
            if subnet_id:
                subnets_with_instances.add(subnet_id)

    return subnets_with_instances


def check_nacl(nacl):
    findings = []

    for entry in nacl.get("Entries", []):
        if entry.get("RuleAction") != "allow":
            continue

        cidr = entry.get("CidrBlock")
        if cidr != "0.0.0.0/0":
            continue

        port_range = entry.get("PortRange")
        
        # Skip "allow all" default rule (important)
        if not port_range:
            continue

        port = port_range.get("From")

        if port == 22:
            findings.append(("CRITICAL", "NACL_SSH_OPEN"))
        elif port == 3389:
            findings.append(("CRITICAL", "NACL_RDP_OPEN"))
        else:
            findings.append(("HIGH", f"NACL_PORT_{port}_OPEN"))

    return findings


def scan(region):
    ec2 = boto3.client("ec2", region_name=region)
    results = []

    active_subnets = get_active_subnets(ec2)
    nacls = ec2.describe_network_acls()["NetworkAcls"]

    for nacl in nacls:
        # Check if NACL is attached to active subnet
        associated = False
        for assoc in nacl.get("Associations", []):
            if assoc.get("SubnetId") in active_subnets:
                associated = True
                break

        if not associated:
            continue  # skip unused infra

        nacl_id = nacl["NetworkAclId"]
        findings = check_nacl(nacl)

        results.append((nacl_id, findings))

    return results