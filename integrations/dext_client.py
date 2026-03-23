"""
Dext (Receipt Bank) API Client

Pulls captured and processed expenses for matching against bank
transactions (missing receipt detection).

Requires: DEXT_API_TOKEN
Get from: Contact Dext partner support (API access is partner-only)
"""

import json
import urllib.request
import urllib.parse
import csv
from datetime import date
from pathlib import Path

try:
    from . import config_template as config
except ImportError:
    import config_template as config


class DextClient:
    """Dext API client for expense data retrieval."""

    def __init__(self):
        self.api_token = config.DEXT_API_TOKEN
        self.base_url = config.DEXT_BASE_URL

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated GET request."""
        url = f"{self.base_url}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def get_expenses(self, start_date: str, end_date: str,
                     status: str = "published") -> list[dict]:
        """Pull processed expenses for a date range.

        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            status: "published" (sent to QBO), "pending", or "all"

        Returns: [
            {
                "date": "2025-01-03",
                "vendor": "SYSCO CANADA",
                "total_amount": 2816.89,
                "subtotal": 2451.11,
                "gst": 122.56,
                "qst": 244.56,
                "gl_account": "5010",
                "category": "COGS-Food",
                "receipt_url": "https://...",
                "gst_number": "123456789RT0001",
                "qst_number": "1234567890TQ0001",
            },
            ...
        ]
        """
        result = self._api_get("items", {
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "per_page": 100,
        })
        return self._parse_expenses(result)

    def get_inbox_items(self) -> list[dict]:
        """Get unprocessed items in the Dext inbox."""
        result = self._api_get("items", {"status": "inbox"})
        return self._parse_inbox(result)

    def get_expense_by_vendor(self, vendor: str, start_date: str,
                               end_date: str) -> list[dict]:
        """Search expenses by vendor name."""
        all_expenses = self.get_expenses(start_date, end_date)
        return [e for e in all_expenses
                if vendor.lower() in e.get("vendor", "").lower()]

    def export_expenses_csv(self, start_date: str, end_date: str,
                            output_dir: Path) -> Path:
        """Export expenses to CSV matching our sample data schema."""
        expenses = self.get_expenses(start_date, end_date)
        output_dir.mkdir(parents=True, exist_ok=True)

        month_str = start_date[:7]  # YYYY-MM
        filepath = output_dir / f"dext_expenses_{month_str}.csv"

        fieldnames = [
            "date", "vendor", "description", "gl_account", "total_amount",
            "subtotal", "gst", "qst", "tax_code", "gst_number", "qst_number",
            "payment_method", "receipt_status",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for e in expenses:
                writer.writerow({
                    "date": e.get("date"),
                    "vendor": e.get("vendor"),
                    "description": e.get("description", ""),
                    "gl_account": e.get("gl_account", ""),
                    "total_amount": f"{e.get('total_amount', 0):.2f}",
                    "subtotal": f"{e.get('subtotal', 0):.2f}",
                    "gst": f"{e.get('gst', 0):.2f}",
                    "qst": f"{e.get('qst', 0):.2f}",
                    "tax_code": e.get("tax_code", "GQ"),
                    "gst_number": e.get("gst_number", ""),
                    "qst_number": e.get("qst_number", ""),
                    "payment_method": e.get("payment_method", ""),
                    "receipt_status": "captured",
                })

        return filepath

    # --- Parsers ---

    def _parse_expenses(self, raw: dict) -> list[dict]:
        """Parse Dext API response into standard format."""
        items = raw.get("data", raw.get("items", []))
        if isinstance(items, dict):
            items = [items]

        expenses = []
        for item in items:
            total = float(item.get("total", item.get("amount", 0)))
            gst = float(item.get("tax1", item.get("gst", 0)))
            qst = float(item.get("tax2", item.get("qst", 0)))
            subtotal = total - gst - qst

            expenses.append({
                "date": item.get("date", item.get("issue_date", "")),
                "vendor": item.get("supplier", item.get("vendor", "")),
                "description": item.get("description", ""),
                "total_amount": total,
                "subtotal": subtotal,
                "gst": gst,
                "qst": qst,
                "gl_account": item.get("category", item.get("gl_code", "")),
                "category": item.get("category_name", ""),
                "receipt_url": item.get("attachment_url", ""),
                "gst_number": item.get("tax_number_1", ""),
                "qst_number": item.get("tax_number_2", ""),
                "payment_method": item.get("payment_method", ""),
                "tax_code": self._determine_tax_code(item),
            })
        return expenses

    def _parse_inbox(self, raw: dict) -> list[dict]:
        """Parse inbox items."""
        items = raw.get("data", [])
        return [
            {
                "id": item.get("id"),
                "vendor": item.get("supplier", "Unknown"),
                "amount": float(item.get("total", 0)),
                "date_received": item.get("created_at"),
                "status": item.get("status", "pending"),
                "issue": item.get("warning", ""),
            }
            for item in items
        ]

    def _determine_tax_code(self, item: dict) -> str:
        """Determine QBO tax code from Dext data."""
        gst = float(item.get("tax1", item.get("gst", 0)))
        qst = float(item.get("tax2", item.get("qst", 0)))
        if gst > 0 and qst > 0:
            return "GQ"  # GST + QST
        elif gst > 0:
            return "G"   # GST only
        elif qst > 0:
            return "Q"   # QST only (unusual)
        else:
            return "E"   # Exempt


def get_client() -> DextClient:
    """Create a Dext client."""
    return DextClient()


if __name__ == "__main__":
    if not config.DEXT_API_TOKEN:
        print("Dext Client — NOT READY")
        print("Missing: DEXT_API_TOKEN")
        print("\nTo set up:")
        print("1. Contact Dext partner support")
        print("2. Request API access for your partner account")
        print("3. Set DEXT_API_TOKEN environment variable")
    else:
        print("Dext Client — credentials found, ready to connect.")
