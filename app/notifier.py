import requests
import json
from app import settings
from app.logger import logger

def format_findings(findings):
    if not findings:
        return ""

    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }

    sorted_findings = sorted(
        findings,
        key=lambda f: severity_order.get(f["severity"], 99)
    )

    lines = []
    for f in sorted_findings:
        lines.append(
            f"[{f['severity']}] {f['resource']} {f['id']} ({f['region']}) - {f['issue']}"
        )

    return "\n\n".join(lines)

def send_slack(findings):
    if not settings.ENABLE_SLACK:
        return
    if not settings.SLACK_WEBHOOK or not findings:
        return

    payload = {"text": format_findings(findings)}
    requests.post(settings.SLACK_WEBHOOK, data=json.dumps(payload))


def send_telegram(findings):
    if not settings.ENABLE_TELEGRAM:
        return
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return
    if not findings:
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": format_findings(findings)
    })


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