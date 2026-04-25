# Alerts Documentation

### Flow

1. Findings generated
2. Filter by severity
3. Format message
4. Send to channels

### Channels

- Slack (webhook)
- Telegram (bot API)

### Behavior

- Config-driven (env vars)
- Message truncation handled (Telegram limit)

### Severity filtering

Only configured severities are sent
