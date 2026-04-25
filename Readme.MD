# InfraGuard

InfraGuard is an AWS security scanner that checks your infrastructure for common misconfigurations and shows results via API and alerts.

---

![Architecture](docs/img/architecture.png)

## What it does

- Scans AWS across multiple regions

- Checks:
  - S3 buckets (public access)
  - EC2 instances (open ports like SSH/RDP)
  - NACL rules
  - Load balancers
  - IAM users/roles (MFA, admin access)
  - RDS (public access, encryption, backups)
  - CloudTrail setup

- Stores findings in PostgreSQL

- Tracks findings lifecycle (OPEN -> RESOLVED)

---

## How it works

- API receives request to start scan
- Scan is pushed to Redis queue
- Worker picks it up and runs scan
- Results are stored in DB
- Alerts are sent (Telegram / Slack)

---

## System behavior

- Scans run asynchronously (non-blocking API)
- Uses retry with delay if something fails (like AWS errors)
- Uses **at-least-once execution** -> scan may run more than once if retry happens
- Uses **idempotency** -> same finding is not duplicated (based on hash)
- Uses **concurrency control** -> only one scan runs at a time (to avoid conflicts)
- Handles crashes -> if worker dies, stuck scans are marked failed

---

## API

Base URL:
`http://localhost:8000/api/v1`

Endpoints:

- `GET /health`
- `POST /scans` -> trigger scan
- `GET /scans` -> list scans
- `GET /scans/{id}` -> scan status
- `GET /findings` -> list findings

Swagger UI:
`http://localhost:8000/docs`

---

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Data Model](docs/data-model.md)
- [Scanner Engine](docs/scanner.md)
- [Worker & Queue](docs/worker.md)
- [Alerts](docs/alerts.md)
- [Tradeoffs](docs/tradeoffs.md)

---

## Demo

![Telegram Alerts](docs/img/telegram.jpeg)

---

## Setup (Docker)

```bash
git clone https://github.com/RutvikMendpara/InfraGuard.git
cd InfraGuard/docker
docker compose up --build
```

---

## Setup (Local)

```bash
git clone https://github.com/RutvikMendpara/InfraGuard.git
cd InfraGuard
pip install -r requirements.txt
cp .env.example .env
```

Run:

```bash
uvicorn app.main:app --reload
```

---

## AWS Setup

Create IAM user with read-only access and attach:

- AmazonEC2ReadOnlyAccess
- AmazonRDSReadOnlyAccess
- AmazonS3ReadOnlyAccess
- AmazonVPCReadOnlyAccess
- AWSCloudTrail_ReadOnlyAccess
- IAMReadOnlyAccess

Add access keys in `.env`.

---

## Config (.env)

- AWS credentials
- DATABASE_URL
- REDIS_URL
- Telegram / Slack config
- Scheduler config

---

## Tech stack

- FastAPI
- PostgreSQL
- Redis (RQ)
- SQLAlchemy
- Docker
- boto3

---

## License

GNU GENERAL PUBLIC LICENSE Version 3
[LICENSE](LICENSE)
