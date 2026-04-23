import boto3


def get_all_regions():
    ec2 = boto3.client("ec2")
    regions = ec2.describe_regions()["Regions"]
    return [r["RegionName"] for r in regions]


def print_findings(resource, name, findings):
    print(f"\n{resource}: {name}")

    if not findings:
        print("Status: SAFE")
        return

    print("Findings:")
    for severity, issue in findings:
        print(f"[{severity}] {issue}")