from concurrent.futures import ThreadPoolExecutor, as_completed
from app import s3, ec2, nacl, elb
from app.utils import get_all_regions, print_findings


MAX_WORKERS = 20  


def scan_region(region):
    output = []
    output.append(f"\n===== REGION: {region} =====")

    # EC2
    ec2_results = ec2.scan(region)
    for instance_id, state, public_ip, findings in ec2_results:
        block = [
            f"\nEC2 Instance: {instance_id}",
            f"State: {state}",
            f"Public IP: {public_ip or 'None'}"
        ]

        if not findings:
            block.append("Status: SAFE")
        else:
            block.append("Findings:")
            for severity, issue in findings:
                block.append(f"[{severity}] {issue}")

        output.extend(block)

    # NACL
    nacl_results = nacl.scan(region)
    for nacl_id, findings in nacl_results:
        block = [f"\nNACL: {nacl_id}"]
        if not findings:
            block.append("Status: SAFE")
        else:
            block.append("Findings:")
            for severity, issue in findings:
                block.append(f"[{severity}] {issue}")
        output.extend(block)

    # ELB
    elb_results = elb.scan(region)
    for lb_name, findings in elb_results:
        block = [f"\nLoadBalancer: {lb_name}"]
        if not findings:
            block.append("Status: SAFE")
        else:
            block.append("Findings:")
            for severity, issue in findings:
                block.append(f"[{severity}] {issue}")
        output.extend(block)

    return "\n".join(output)


def main():
    # ---------- S3 (sequential) ----------
    print("===== S3 SCAN =====")
    s3_results = s3.scan()

    for name, findings in s3_results:
        print_findings("S3 Bucket", name, findings)

    # ---------- PARALLEL REGION SCAN ----------
    regions = get_all_regions()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}

        for region in regions:
            future = executor.submit(scan_region, region)
            futures[future] = region

        for future in as_completed(futures):
            region = futures[future]
            try:
                print(future.result())
            except Exception as e:
                print(f"\n===== REGION: {region} FAILED =====")
                print(f"Error: {e}")


if __name__ == "__main__":
    main()