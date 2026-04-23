# InfraGuard

InfraGuard is a lightweight AWS security scanner that detects common misconfigurations across services like EC2, S3, ELB, and NACL.

It scans your infrastructure periodically and sends alerts to Slack or Telegram for high-risk issues.

---

## Features

- Multi-region AWS scanning
- Detects:
  - Public S3 buckets
  - Open security groups (SSH/RDP/ports)
  - Risky NACL rules
  - Internet-facing load balancers with open access

- Severity-based alerts (CRITICAL, HIGH, etc.)
- Telegram / Slack notifications
- Configurable scan interval

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/RutvikMendpara/InfraGuard.git
cd infraguard
pip install -r requirements.txt
```

---

### 2. Configure environment

Copy example file:

```bash
cp .env.example .env
```

---

### 3. AWS setup

Create an IAM user with **read-only access**:

- Go to AWS IAM -> Users -> Create User
- Attach policy: `ReadOnlyAccess`
- Generate access keys
- Use those keys in `.env`

---

## Run

```bash
python main.py
```

---

## Notes

- Alerts are sent only for selected severities (`ALERT_SEVERITIES`)
- Default scan interval: 1 hour
- Designed for small to medium AWS accounts

---
