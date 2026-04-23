import os
from dotenv import load_dotenv

load_dotenv()

# GENERAL
APP_NAME = "InfraGuard"

# SCAN SETTINGS
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 10))
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", 21600)) # default = 6h

# ALERT SETTINGS
ENABLE_ALERTS = os.getenv("ENABLE_ALERTS", "true").lower() == "true"

ALERT_SEVERITIES = os.getenv(
    "ALERT_SEVERITIES",
    "CRITICAL,HIGH"
).split(",")

# CHANNEL TOGGLES
ENABLE_SLACK = os.getenv("ENABLE_SLACK", "true").lower() == "true"
ENABLE_TELEGRAM = os.getenv("ENABLE_TELEGRAM", "false").lower() == "true"

# SECRETS 
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")