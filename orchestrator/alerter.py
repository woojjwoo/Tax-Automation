"""
Alert System — Slack and Email Notifications

Sends alerts when automation detects issues:
- Sync failures
- Missing receipts
- Bank feed disconnections
- Approaching deadlines
- Tip attribution flags

Usage:
    from orchestrator.alerter import send_alert, AlertLevel

    send_alert(
        level=AlertLevel.CRITICAL,
        title="QBO Sync Failure",
        message="January 8 revenue not posted to QBO",
        details={"missing_revenue": 1072.00},
    )
"""

import json
import smtplib
import urllib.request
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from integrations import config_template as config
except ImportError:
    from integrations import config_template as config


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


# Slack colors by level
SLACK_COLORS = {
    AlertLevel.INFO: "#36a64f",      # green
    AlertLevel.WARNING: "#daa520",    # gold
    AlertLevel.HIGH: "#ff8c00",      # dark orange
    AlertLevel.CRITICAL: "#dc143c",  # crimson
}

# Alert log
ALERT_LOG = Path(__file__).parent.parent / "logs" / "alerts.jsonl"


def send_alert(level: AlertLevel, title: str, message: str,
               details: dict = None, channels: list[str] = None):
    """Send an alert via configured channels.

    Args:
        level: AlertLevel enum
        title: Short title (e.g., "QBO Sync Failure")
        message: Description of the issue
        details: Optional structured data
        channels: Override channels ("slack", "email", "log"). Default: all configured.
    """
    if channels is None:
        channels = []
        if config.SLACK_WEBHOOK_URL:
            channels.append("slack")
        if config.SMTP_USER:
            channels.append("email")
        channels.append("log")  # Always log

    alert_data = {
        "timestamp": datetime.now().isoformat(),
        "level": level.value,
        "title": title,
        "message": message,
        "details": details or {},
    }

    results = {}

    if "slack" in channels:
        results["slack"] = _send_slack(level, title, message, details)

    if "email" in channels:
        results["email"] = _send_email(level, title, message, details)

    if "log" in channels:
        results["log"] = _log_alert(alert_data)

    # Console output
    icon = {"info": "[i]", "warning": "[!]", "high": "[!!]", "critical": "[!!!]"}
    print(f"{icon.get(level.value, '[?]')} {level.value.upper()}: {title}")
    print(f"    {message}")
    if details:
        for k, v in details.items():
            print(f"    {k}: {v}")

    return results


def _send_slack(level: AlertLevel, title: str, message: str,
                details: dict = None) -> bool:
    """Send Slack notification via webhook."""
    if not config.SLACK_WEBHOOK_URL:
        return False

    # Build attachment fields from details
    fields = []
    if details:
        for k, v in details.items():
            fields.append({
                "title": k.replace("_", " ").title(),
                "value": str(v),
                "short": True,
            })

    payload = {
        "channel": config.SLACK_CHANNEL,
        "username": "Giwa Tax Bot",
        "icon_emoji": ":receipt:",
        "attachments": [{
            "color": SLACK_COLORS.get(level, "#808080"),
            "title": f"{level.value.upper()}: {title}",
            "text": message,
            "fields": fields,
            "footer": "Giwa Restaurant Tax Automation",
            "ts": int(datetime.now().timestamp()),
        }],
    }

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            config.SLACK_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"  Slack alert failed: {e}")
        return False


def _send_email(level: AlertLevel, title: str, message: str,
                details: dict = None) -> bool:
    """Send email notification via SMTP."""
    if not config.SMTP_USER or not config.ALERT_RECIPIENTS:
        return False

    subject = f"[{level.value.upper()}] Giwa: {title}"

    # Build HTML body
    detail_rows = ""
    if details:
        for k, v in details.items():
            detail_rows += f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
    <h2 style="color: {SLACK_COLORS.get(level, '#808080')};">
        {level.value.upper()}: {title}
    </h2>
    <p>{message}</p>
    {"<table border='1' cellpadding='8' cellspacing='0'>" + detail_rows + "</table>" if detail_rows else ""}
    <hr>
    <p style="color: #888; font-size: 12px;">
        Giwa Restaurant Tax Automation — {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_USER
    msg["To"] = ", ".join(config.ALERT_RECIPIENTS)
    msg.attach(MIMEText(message, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, config.ALERT_RECIPIENTS, msg.as_string())
        return True
    except Exception as e:
        print(f"  Email alert failed: {e}")
        return False


def _log_alert(alert_data: dict) -> bool:
    """Append alert to JSONL log file."""
    try:
        ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ALERT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert_data) + "\n")
        return True
    except Exception as e:
        print(f"  Log alert failed: {e}")
        return False


# --- Convenience functions for common alerts ---

def alert_sync_failure(date_str: str, missing_revenue: float,
                       missing_gst: float, missing_qst: float):
    """Alert: Lightspeed → QBO sync failed for a day."""
    send_alert(
        level=AlertLevel.CRITICAL,
        title="QBO Sync Failure",
        message=f"SRM recorded revenue on {date_str} but no corresponding "
                f"QBO posting found. Revenue is not being tracked.",
        details={
            "date": date_str,
            "missing_revenue": f"${missing_revenue:,.2f}",
            "missing_gst": f"${missing_gst:,.2f}",
            "missing_qst": f"${missing_qst:,.2f}",
            "action": "Re-sync Lightspeed or create manual journal entry",
        },
    )


def alert_missing_receipts(count: int, total_amount: float,
                           annual_tax_loss: float):
    """Alert: Bank transactions without matching Dext receipts."""
    send_alert(
        level=AlertLevel.WARNING,
        title="Missing Receipts Detected",
        message=f"{count} bank transaction(s) have no matching Dext receipt.",
        details={
            "missing_count": count,
            "total_unmatched": f"${total_amount:,.2f}",
            "projected_annual_tax_loss": f"${annual_tax_loss:,.2f}",
            "action": "Find receipts or request duplicates from vendors",
        },
    )


def alert_bank_feed_down(account_name: str, last_sync_date: str):
    """Alert: QBO bank feed disconnected."""
    send_alert(
        level=AlertLevel.WARNING,
        title="Bank Feed Disconnected",
        message=f"QBO bank feed for '{account_name}' last synced on "
                f"{last_sync_date}. Transactions may be missing.",
        details={
            "account": account_name,
            "last_sync": last_sync_date,
            "action": "Reconnect in QBO → Banking (see bank_feed_reconnection_guide.md)",
        },
    )


def alert_deadline_approaching(filing_type: str, due_date: str,
                                days_remaining: int):
    """Alert: Tax filing deadline approaching."""
    level = AlertLevel.CRITICAL if days_remaining <= 3 else \
            AlertLevel.HIGH if days_remaining <= 7 else \
            AlertLevel.WARNING if days_remaining <= 14 else AlertLevel.INFO

    send_alert(
        level=level,
        title=f"{filing_type} Due in {days_remaining} Days",
        message=f"{filing_type} filing is due on {due_date}.",
        details={
            "filing_type": filing_type,
            "due_date": due_date,
            "days_remaining": days_remaining,
        },
    )


def alert_tip_attribution(employee_name: str, shortfall: float,
                           pay_period: str):
    """Alert: Employee tip attribution required."""
    send_alert(
        level=AlertLevel.INFO,
        title="Tip Attribution Required",
        message=f"{employee_name} declared tips below 8% minimum for "
                f"pay period {pay_period}.",
        details={
            "employee": employee_name,
            "shortfall": f"${shortfall:,.2f}",
            "pay_period": pay_period,
            "action": "Attribute shortfall amount via payroll system",
        },
    )


if __name__ == "__main__":
    print("Testing alert system (log-only mode)...\n")
    send_alert(
        level=AlertLevel.CRITICAL,
        title="Test Alert — QBO Sync Failure",
        message="This is a test alert. SRM recorded $1,072 on 2025-01-08 "
                "but no QBO posting found.",
        details={"missing_revenue": "$1,072.00", "test": True},
        channels=["log"],
    )
    print(f"\nAlert logged to: {ALERT_LOG}")
