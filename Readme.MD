# InfraGuard

InfraGuard is an AWS security scanning service that detects infrastructure misconfigurations and exposes findings via API and alerts.

## Features

- Scans AWS across regions
- Checks:
  - S3 public access
  - EC2 open ports (SSH/RDP)
  - NACL rules
  - Load balancer exposure
  - IAM issues (admin roles, MFA)
  - RDS security
  - CloudTrail status
- Stores findings in PostgreSQL
- Tracks lifecycle (OPEN -> RESOLVED)
- Async scan execution (queue + worker)
- Scheduled scans (optional)
- Slack / Telegram alerts
- REST API with filtering and pagination

## Architecture

```

API (FastAPI) -> Queue (Redis) -> Worker -> AWS Scan -> PostgreSQL -> Alerts

```

## Demo

![Telegram Alerts](docs/img/telegram.jpeg)

## API

Base URL:  
http://localhost:8000/api/v1

### Endpoints

- `GET /health`
- `POST /scans` — trigger scan (async)
- `GET /scans` — list scans
- `GET /scans/{id}` — scan status
- `GET /findings` — list findings

Swagger UI:  
http://localhost:8000/docs

## Setup (Docker)

```bash
git clone https://github.com/RutvikMendpara/InfraGuard.git
cd InfraGuard/docker
docker compose up --build

```

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

## AWS Setup

Create an IAM user with read-only access and attach:

- AmazonEC2ReadOnlyAccess
- AmazonRDSReadOnlyAccess
- AmazonS3ReadOnlyAccess
- AmazonVPCReadOnlyAccess
- AWSCloudTrail_ReadOnlyAccess
- IAMReadOnlyAccess

Generate access keys and add them to `.env`.

## Configuration

Update `.env` with:

- AWS credentials
- `DATABASE_URL`
- `REDIS_URL`
- Alert settings (Slack / Telegram)
- Scheduler config (optional)

## Tech Stack

- FastAPI
- PostgreSQL
- Redis (RQ)
- SQLAlchemy
- Docker
- boto3

## License

GNU GENERAL PUBLIC LICENSE Version 3
[LICENSE](LICENSE)
