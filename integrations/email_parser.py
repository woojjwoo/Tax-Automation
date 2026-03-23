"""
Email Parser for DoorDash and Skip The Dishes Payout Reports

These platforms don't have public APIs, so we parse their payout
notification emails instead. Connects via IMAP, finds payout emails,
extracts amounts from the email body or PDF attachment.

Requires: EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_IMAP_HOST
"""

import csv
import email
import imaplib
import re
from datetime import date
from email.header import decode_header
from pathlib import Path

try:
    from . import config_template as config
except ImportError:
    import config_template as config


class EmailPayoutParser:
    """Parse delivery platform payout emails via IMAP."""

    # Email sender patterns for each platform
    PLATFORM_SENDERS = {
        "doordash": [
            "no-reply@doordash.com",
            "payments@doordash.com",
            "merchant-payments@doordash.com",
        ],
        "skip": [
            "no-reply@skipthedishes.com",
            "payments@skipthedishes.com",
            "merchant@skipthedishes.com",
        ],
    }

    # Regex patterns to extract payout amounts from email body
    AMOUNT_PATTERNS = {
        "doordash": [
            r"(?:payout|deposit|payment)[:\s]*\$?([\d,]+\.?\d*)",
            r"(?:net|total)[:\s]*\$?([\d,]+\.?\d*)",
            r"\$?([\d,]+\.?\d*)\s*(?:has been|will be)\s*(?:deposited|transferred)",
        ],
        "skip": [
            r"(?:payout|deposit|payment)[:\s]*\$?([\d,]+\.?\d*)",
            r"(?:net|total)[:\s]*\$?([\d,]+\.?\d*)",
            r"\$?([\d,]+\.?\d*)\s*(?:deposited|transferred)",
        ],
    }

    COMMISSION_PATTERNS = {
        "doordash": [
            r"(?:commission|fee|marketplace fee)[:\s]*\$?([\d,]+\.?\d*)",
        ],
        "skip": [
            r"(?:commission|fee|service fee)[:\s]*\$?([\d,]+\.?\d*)",
        ],
    }

    GROSS_PATTERNS = {
        "doordash": [
            r"(?:gross|subtotal|total sales|order total)[:\s]*\$?([\d,]+\.?\d*)",
        ],
        "skip": [
            r"(?:gross|subtotal|total sales)[:\s]*\$?([\d,]+\.?\d*)",
        ],
    }

    def __init__(self):
        self.imap_host = config.EMAIL_IMAP_HOST
        self.imap_port = config.EMAIL_IMAP_PORT
        self.email_address = config.EMAIL_ADDRESS
        self.email_password = config.EMAIL_PASSWORD
        self.connection = None

    def connect(self):
        """Connect to IMAP server."""
        self.connection = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        self.connection.login(self.email_address, self.email_password)

    def disconnect(self):
        """Disconnect from IMAP server."""
        if self.connection:
            self.connection.logout()
            self.connection = None

    def fetch_payout_emails(self, platform: str, since_date: str,
                            before_date: str = None) -> list[dict]:
        """Fetch and parse payout emails for a platform.

        Args:
            platform: "doordash" or "skip"
            since_date: YYYY-MM-DD
            before_date: YYYY-MM-DD (optional)

        Returns: [
            {
                "platform": "doordash",
                "email_date": "2025-01-11",
                "subject": "Your weekly payout is ready",
                "gross_sales": 165.00,
                "commission": 41.25,
                "net_deposit": 123.75,
                "raw_body": "...",
            },
        ]
        """
        if not self.connection:
            self.connect()

        self.connection.select("INBOX")

        senders = self.PLATFORM_SENDERS.get(platform, [])
        all_payouts = []

        for sender in senders:
            # Build IMAP search query
            criteria = f'(FROM "{sender}" SINCE "{self._format_imap_date(since_date)}"'
            if before_date:
                criteria += f' BEFORE "{self._format_imap_date(before_date)}"'
            criteria += ")"

            try:
                _status, messages = self.connection.search(None, criteria)
            except imaplib.IMAP4.error:
                continue

            msg_ids = messages[0].split()

            for msg_id in msg_ids:
                _status, msg_data = self.connection.fetch(msg_id, "(RFC822)")
                raw_email = msg_data[0][1]
                parsed = self._parse_email(raw_email, platform)
                if parsed:
                    all_payouts.append(parsed)

        return all_payouts

    def _parse_email(self, raw_email: bytes, platform: str) -> dict | None:
        """Parse a single payout email."""
        msg = email.message_from_bytes(raw_email)

        subject = self._decode_header(msg["Subject"])
        email_date = msg["Date"]

        # Skip non-payout emails
        payout_keywords = ["payout", "payment", "deposit", "weekly", "earnings"]
        if not any(kw in subject.lower() for kw in payout_keywords):
            return None

        # Extract body text
        body = self._get_email_body(msg)
        if not body:
            return None

        # Extract amounts using regex
        net_deposit = self._extract_amount(body, self.AMOUNT_PATTERNS.get(platform, []))
        commission = self._extract_amount(body, self.COMMISSION_PATTERNS.get(platform, []))
        gross_sales = self._extract_amount(body, self.GROSS_PATTERNS.get(platform, []))

        # If we have net and commission but not gross, calculate it
        if net_deposit and commission and not gross_sales:
            gross_sales = net_deposit + commission
        # If we have gross and commission but not net, calculate it
        elif gross_sales and commission and not net_deposit:
            net_deposit = gross_sales - commission

        if not net_deposit:
            return None  # Can't use this email without at least the net amount

        return {
            "platform": platform,
            "email_date": email_date,
            "subject": subject,
            "gross_sales": gross_sales or 0.0,
            "commission": commission or 0.0,
            "net_deposit": net_deposit,
            "raw_body": body[:500],  # First 500 chars for debugging
        }

    def _extract_amount(self, text: str, patterns: list[str]) -> float | None:
        """Extract a dollar amount from text using regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        return None

    def _get_email_body(self, msg: email.message.Message) -> str:
        """Extract plain text body from email."""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode("utf-8", errors="replace")
                elif content_type == "text/html":
                    # Fallback to HTML, strip tags
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode("utf-8", errors="replace")
                        return re.sub(r"<[^>]+>", " ", html)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8", errors="replace")
        return ""

    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        if not header:
            return ""
        decoded_parts = decode_header(header)
        result = ""
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result += part.decode(charset or "utf-8", errors="replace")
            else:
                result += part
        return result

    def _format_imap_date(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to IMAP date format (DD-Mon-YYYY)."""
        d = date.fromisoformat(date_str)
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{d.day:02d}-{months[d.month - 1]}-{d.year}"

    def export_payouts_csv(self, platform: str, payouts: list[dict],
                           output_dir: Path) -> Path:
        """Export parsed payouts to CSV for reconciliation."""
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"{platform}_payouts_parsed.csv"

        fieldnames = [
            "platform", "email_date", "subject",
            "gross_sales", "commission", "net_deposit",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in payouts:
                writer.writerow({k: p.get(k, "") for k in fieldnames})

        return filepath


def get_parser() -> EmailPayoutParser:
    """Create an email parser."""
    return EmailPayoutParser()


if __name__ == "__main__":
    if not config.EMAIL_ADDRESS:
        print("Email Parser — NOT READY")
        print("Missing: EMAIL_ADDRESS, EMAIL_PASSWORD")
        print("\nTo set up:")
        print("1. Create a dedicated email (e.g., giwa-finance@gmail.com)")
        print("2. Enable IMAP access in email settings")
        print("3. Generate an app-specific password (Gmail: Security → App passwords)")
        print("4. Forward DoorDash/Skip payout emails to this inbox")
        print("5. Set environment variables")
    else:
        print("Email Parser — credentials found, ready to connect.")
