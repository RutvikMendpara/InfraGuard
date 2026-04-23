import boto3


def check_security_group(sg):
    findings = []

    for perm in sg.get("IpPermissions", []):
        from_port = perm.get("FromPort")
        to_port = perm.get("ToPort")

        for ip_range in perm.get("IpRanges", []):
            if ip_range.get("CidrIp") == "0.0.0.0/0":
                if from_port == 22:
                    findings.append(("CRITICAL", "SSH_OPEN"))
                elif from_port == 3389:
                    findings.append(("CRITICAL", "RDP_OPEN"))
                else:
                    findings.append(("HIGH", f"PORT_{from_port}_OPEN"))

        for ipv6 in perm.get("Ipv6Ranges", []):
            if ipv6.get("CidrIpv6") == "::/0":
                findings.append(("CRITICAL", "IPV6_OPEN"))

    return findings


def scan(region):
    ec2 = boto3.client("ec2", region_name=region)
    results = []

    reservations = ec2.describe_instances()["Reservations"]

    for res in reservations:
        for instance in res["Instances"]:
            instance_id = instance["InstanceId"]
            public_ip = instance.get("PublicIpAddress")
            state = instance["State"]["Name"]  # <-- NEW

            findings = []

            for sg in instance.get("SecurityGroups", []):
                sg_id = sg["GroupId"]
                sg_data = ec2.describe_security_groups(GroupIds=[sg_id])["SecurityGroups"][0]
                findings.extend(check_security_group(sg_data))

            if public_ip and findings:
                findings.append(("CRITICAL", "PUBLIC_INSTANCE_WITH_OPEN_PORTS"))

            results.append((instance_id, state, public_ip, findings))

    return results