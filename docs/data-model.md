# Data Model documentation

### Tables

#### findings

- id (uuid)
- resource_type
- resource_id
- region
- severity
- issue
- status (OPEN, RESOLVED)
- hash (unique)
- first_seen_at
- last_seen_at

**Important**

- `hash` ensures idempotency
- Unique constraint avoids duplicates

#### scan_runs

- id
- status (PENDING, RUNNING, SUCCESS, FAILED, RETRYING)
- started_at
- completed_at
- total_findings
- retry_count

### Lifecycle

Findings:

- New -> OPEN
- Missing in next scan -> RESOLVED

Scans:

- PENDING -> RUNNING -> SUCCESS/FAILED
