# Scanner Documentation

### Structure

Each AWS service has its own scanner module.

Examples:

- [ec2](../app/aws/ec2.py)
- [s3](../app/aws/s3.py)
- [iam](../app/aws/iam.py)
- [rds](../app/aws/rds.py)

### Pattern

Each scanner:

1. Fetch resources using boto3
2. Apply security checks
3. Generate findings

Output format:

```
{
  resource_type,
  resource_id,
  region,
  severity,
  issue,
  status
}
```

### Region parallelization

- Uses ThreadPoolExecutor
- Each region scanned independently

### Extensibility

To add new scanner:

- Create new module
- Implement `scan()`
- Add to scanner service
