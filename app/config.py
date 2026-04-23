import os
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

AWS_CONFIG = Config(
    retries={"max_attempts": 10, "mode": "adaptive"}
)

MAX_WORKERS = 10

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SCAN_INTERVAL_SECONDS = 6 * 60 * 60