# API Documentation

### Base URL

`/api/v1`

### Endpoints

#### Health

GET `/health`

- Response: `{ "status": "ok" }`

#### Trigger Scan

POST `/scans`

- Creates a scan and enqueues job
- Error: 409 if scan already running

#### List Scans

GET `/scans`

- Returns all scan runs

#### Get Scan

GET `/scans/{id}`

- Returns scan status

#### List Findings

GET `/findings`

Query params:

- severity
- status
- region
- resource_type
- sort_by (first_seen_at, last_seen_at, severity)
- desc (bool)
- limit (1-100)
- offset

### Notes

- Pagination is offset-based
- Sorting is DB-driven
- Filters are optional
