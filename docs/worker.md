# Worker Documentation

### Flow

1. Job pulled from Redis
2. Scan marked RUNNING
3. Scanner executes
4. Findings stored
5. Alerts triggered
6. Scan marked SUCCESS

### Retry behavior

- Max retries: 3
- Delays: 30s, 60s, 120s

### Failure handling

- If retries left -> RETRYING
- Else -> FAILED

### Guarantees

- At-least-once execution
- Idempotency handled at DB level
