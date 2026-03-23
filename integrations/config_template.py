"""
Central configuration for all integrations and automation.

Copy this file to config.py and fill in your credentials.
NEVER commit config.py — only config_template.py goes in git.
"""

import os
from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"

# --- QuickBooks Online ---
QBO_CLIENT_ID = os.environ.get("QBO_CLIENT_ID", "")
QBO_CLIENT_SECRET = os.environ.get("QBO_CLIENT_SECRET", "")
QBO_REALM_ID = os.environ.get("QBO_REALM_ID", "")  # Company ID
QBO_REFRESH_TOKEN = os.environ.get("QBO_REFRESH_TOKEN", "")
QBO_ENVIRONMENT = os.environ.get("QBO_ENVIRONMENT", "sandbox")  # "sandbox" or "production"
QBO_REDIRECT_URI = os.environ.get("QBO_REDIRECT_URI", "http://localhost:8080/callback")

# --- Lightspeed Restaurant ---
LIGHTSPEED_API_KEY = os.environ.get("LIGHTSPEED_API_KEY", "")
LIGHTSPEED_ACCOUNT_ID = os.environ.get("LIGHTSPEED_ACCOUNT_ID", "")
LIGHTSPEED_BASE_URL = "https://api.lightspeedrestaurantapp.com"

# --- Dext (Receipt Bank) ---
DEXT_API_TOKEN = os.environ.get("DEXT_API_TOKEN", "")
DEXT_BASE_URL = "https://api.dext.com/v1"

# --- Uber Eats ---
UBER_EATS_CLIENT_ID = os.environ.get("UBER_EATS_CLIENT_ID", "")
UBER_EATS_CLIENT_SECRET = os.environ.get("UBER_EATS_CLIENT_SECRET", "")
UBER_EATS_STORE_ID = os.environ.get("UBER_EATS_STORE_ID", "")

# --- Wagepoint ---
WAGEPOINT_API_KEY = os.environ.get("WAGEPOINT_API_KEY", "")
WAGEPOINT_COMPANY_ID = os.environ.get("WAGEPOINT_COMPANY_ID", "")
WAGEPOINT_BASE_URL = "https://api.wagepoint.com/v1"

# --- Email (for DoorDash/Skip payout parsing) ---
EMAIL_IMAP_HOST = os.environ.get("EMAIL_IMAP_HOST", "imap.gmail.com")
EMAIL_IMAP_PORT = int(os.environ.get("EMAIL_IMAP_PORT", "993"))
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")  # App-specific password

# --- Slack Alerts ---
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL", "#giwa-finance")

# --- Email Alerts ---
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
ALERT_RECIPIENTS = [
    "bookkeeper@giwa.ca",
    "cpa@firm.ca",
]

# --- Giwa Restaurant Business Info ---
BUSINESS = {
    "name": "Giwa Restaurant Inc.",
    "gst_number": os.environ.get("GIWA_GST_NUMBER", ""),
    "qst_number": os.environ.get("GIWA_QST_NUMBER", ""),
    "neq_number": os.environ.get("GIWA_NEQ_NUMBER", ""),
    "fiscal_year_end": "12-31",  # December 31
    "province": "QC",
    "filing_frequency_gst": "monthly",  # or "quarterly"
    "filing_frequency_qst": "monthly",
}

# --- Tax Rates (2025) ---
GST_RATE = 0.05
QST_RATE = 0.09975
TIP_MINIMUM_RATE = 0.08

# --- Delivery Platforms ---
DELIVERY_PLATFORMS = {
    "uber_eats": {
        "commission_rate": 0.30,
        "gl_revenue": "4050",
        "gl_commission": "5310",
    },
    "doordash": {
        "commission_rate": 0.25,
        "gl_revenue": "4060",
        "gl_commission": "5320",
    },
    "skip": {
        "commission_rate": 0.25,
        "gl_revenue": "4070",
        "gl_commission": "5330",
    },
}

# --- GL Account Map ---
GL_ACCOUNTS = {
    "sales_dine_in": "4010",
    "sales_takeout": "4020",
    "sales_delivery": "4050",
    "cogs_food": "5010",
    "cogs_beverage": "5020",
    "cogs_supplies": "5030",
    "wages_kitchen": "5110",
    "wages_service": "5120",
    "wages_management": "5130",
    "rent": "5200",
    "utilities": "5210",
    "insurance": "5220",
    "delivery_commission": "5310",
    "gst_collected": "2310",
    "qst_collected": "2320",
    "gst_itc": "1310",
    "qst_itr": "1320",
}


def validate_config() -> list[str]:
    """Check which credentials are missing. Returns list of missing items."""
    missing = []
    checks = {
        "QBO_CLIENT_ID": QBO_CLIENT_ID,
        "QBO_CLIENT_SECRET": QBO_CLIENT_SECRET,
        "QBO_REALM_ID": QBO_REALM_ID,
        "LIGHTSPEED_API_KEY": LIGHTSPEED_API_KEY,
        "DEXT_API_TOKEN": DEXT_API_TOKEN,
        "UBER_EATS_CLIENT_ID": UBER_EATS_CLIENT_ID,
        "WAGEPOINT_API_KEY": WAGEPOINT_API_KEY,
        "SLACK_WEBHOOK_URL": SLACK_WEBHOOK_URL,
        "GIWA_GST_NUMBER": BUSINESS["gst_number"],
        "GIWA_QST_NUMBER": BUSINESS["qst_number"],
    }
    for name, value in checks.items():
        if not value:
            missing.append(name)
    return missing


if __name__ == "__main__":
    missing = validate_config()
    if missing:
        print(f"Missing {len(missing)} credential(s):")
        for m in missing:
            print(f"  [ ] {m}")
    else:
        print("All credentials configured.")
