import os
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # -------- GENERAL --------
    APP_NAME: str = "InfraGuard"

    # -------- DATABASE --------
    DATABASE_URL: str = os.getenv("DATABASE_URL") # type: ignore

    # -------- AWS --------
    AWS_CONFIG = Config(
        retries={"max_attempts": 10, "mode": "adaptive"}
    )

    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", 10))

    # -------- ALERT SETTINGS --------
    ENABLE_ALERTS: bool = os.getenv("ENABLE_ALERTS", "true").lower() == "true"

    ALERT_SEVERITIES: list[str] = os.getenv(
        "ALERT_SEVERITIES",
        "CRITICAL,HIGH"
    ).split(",")

    # -------- NOTIFICATIONS --------
    ENABLE_SLACK: bool = os.getenv("ENABLE_SLACK", "true").lower() == "true"
    ENABLE_TELEGRAM: bool = os.getenv("ENABLE_TELEGRAM", "false").lower() == "true"

    SLACK_WEBHOOK: str | None = os.getenv("SLACK_WEBHOOK")
    TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str | None = os.getenv("TELEGRAM_CHAT_ID")

    # -------- SCAN --------
    SCAN_INTERVAL_SECONDS: int = int(
        os.getenv("SCAN_INTERVAL_SECONDS", 21600)
    )

    # -------- REDIS --------

    REDIS_URL : str | None = os.getenv("REDIS_URL")

    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"


settings = Settings()