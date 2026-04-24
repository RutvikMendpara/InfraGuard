import requests
import json

from app.core.config import settings
from app.core.logger import logger


def format_findings(findings):
    if not findings:
        return ""

    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    sorted_findings = sorted(
        findings,
        key=lambda f: severity_order.get(f["severity"], 99),
    )

    lines = []
    for f in sorted_findings:
        lines.append(
            f"[{f['severity']}] {f['resource_type']} {f['resource_id']} "
            f"({f['region']}) - {f['issue']}"
        )

    return "\n\n".join(lines)


def send_slack(findings):
    if not settings.ENABLE_SLACK:
        return
    if not settings.SLACK_WEBHOOK or not findings:
        return

    try:
        payload = {"text": format_findings(findings)}
        requests.post(
            settings.SLACK_WEBHOOK,
            data=json.dumps(payload),
            timeout=5,
        )
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")


def send_telegram(findings):
    if not settings.ENABLE_TELEGRAM:
        logger.info("Telegram disabled")
        return

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.error("Telegram config missing")
        return

    if not findings:
        logger.info("No findings to send")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    
    MAX_LEN = 4000
    message = format_findings(findings)

    if len(message) > MAX_LEN:
        message = message[:MAX_LEN] + "\n...truncated"

    logger.info(f"Sending Telegram message:\n{message}")

    try:
        response = requests.post(
            url,
            data={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=10
        )

        logger.info(f"Telegram status: {response.status_code}")
        logger.info(f"Telegram response: {response.text}")

        if response.status_code != 200:
            logger.error("Telegram request failed")

    except Exception as e:
        logger.error(f"Telegram exception: {e}")


def notify(findings):
    if not settings.ENABLE_ALERTS:
        logger.info("Alerts disabled")
        return

    if not findings:
        logger.info("No alert-worthy findings")
        return

    logger.info(f"Sending {len(findings)} alerts")

    send_slack(findings)
    send_telegram(findings)