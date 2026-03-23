"""
Lightspeed Restaurant API Client

Pulls daily sales, SRM summaries, and employee clock-out data
for sync health checks and tip declaration workflows.

Requires: LIGHTSPEED_API_KEY, LIGHTSPEED_ACCOUNT_ID
Get from: Lightspeed back-office → Settings → API Access
"""

import json
import urllib.request
import urllib.parse
import csv
from datetime import date, datetime
from pathlib import Path

try:
    from . import config_template as config
except ImportError:
    import config_template as config


class LightspeedClient:
    """Lightspeed Restaurant API client."""

    def __init__(self):
        self.api_key = config.LIGHTSPEED_API_KEY
        self.account_id = config.LIGHTSPEED_ACCOUNT_ID
        self.base_url = f"{config.LIGHTSPEED_BASE_URL}/api/account/{self.account_id}"

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated GET request."""
        url = f"{self.base_url}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def get_daily_sales(self, target_date: str) -> dict:
        """Pull sales summary for a single day.

        Returns: {
            "date": "2025-01-15",
            "gross_sales": 1385.00,
            "net_sales": 1205.00,
            "gst_collected": 60.25,
            "qst_collected": 120.22,
            "tips": 210.50,
            "voids": 0,
            "refunds": 0,
            "transaction_count": 52,
        }
        """
        result = self._api_get("reports/sales", {
            "startDate": target_date,
            "endDate": target_date,
        })
        return self._parse_daily_sales(result, target_date)

    def get_sales_range(self, start_date: str, end_date: str) -> list[dict]:
        """Pull daily sales for a date range."""
        result = self._api_get("reports/sales", {
            "startDate": start_date,
            "endDate": end_date,
            "groupBy": "day",
        })
        return self._parse_sales_range(result)

    def get_srm_summary(self, start_date: str, end_date: str) -> dict:
        """Pull SRM/MEV summary for the period (signed transaction totals)."""
        result = self._api_get("reports/srm", {
            "startDate": start_date,
            "endDate": end_date,
        })
        return result

    def get_employee_clockouts(self, target_date: str) -> list[dict]:
        """Get employee clock-out events for tip declaration prompts.

        Returns: [
            {"employee_id": "E004", "name": "Server A", "clock_out": "22:15",
             "shift_sales": 450.00, "cc_tips": 72.00},
        ]
        """
        result = self._api_get("employees/shifts", {
            "date": target_date,
            "status": "completed",
        })
        return self._parse_clockouts(result)

    def get_employee_shift_sales(self, employee_id: str,
                                  target_date: str) -> dict:
        """Get sales attributed to a specific employee for a shift."""
        result = self._api_get(f"reports/sales/employee/{employee_id}", {
            "startDate": target_date,
            "endDate": target_date,
        })
        return result

    def export_daily_csv(self, target_date: str, output_dir: Path) -> Path:
        """Export daily sales to CSV format matching our sample data schema."""
        sales = self.get_daily_sales(target_date)
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"srm_daily_{target_date}.csv"

        fieldnames = [
            "date", "day_of_week", "gross_sales", "voids", "refunds",
            "net_sales", "gst_collected", "qst_collected", "total_tips",
            "cash_sales", "credit_card_sales", "transaction_count",
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "date": sales.get("date", target_date),
                "day_of_week": datetime.strptime(target_date, "%Y-%m-%d").strftime("%A"),
                "gross_sales": f"{sales.get('gross_sales', 0):.2f}",
                "voids": f"{sales.get('voids', 0):.2f}",
                "refunds": f"{sales.get('refunds', 0):.2f}",
                "net_sales": f"{sales.get('net_sales', 0):.2f}",
                "gst_collected": f"{sales.get('gst_collected', 0):.2f}",
                "qst_collected": f"{sales.get('qst_collected', 0):.2f}",
                "total_tips": f"{sales.get('tips', 0):.2f}",
                "cash_sales": f"{sales.get('cash_sales', 0):.2f}",
                "credit_card_sales": f"{sales.get('credit_card_sales', 0):.2f}",
                "transaction_count": sales.get("transaction_count", 0),
            })

        return filepath

    # --- Parsers ---

    def _parse_daily_sales(self, raw: dict, target_date: str) -> dict:
        """Parse Lightspeed API response into our standard format."""
        # Lightspeed response structure varies — this handles the common format
        data = raw.get("data", raw)
        return {
            "date": target_date,
            "gross_sales": float(data.get("grossSales", 0)),
            "net_sales": float(data.get("netSales", 0)),
            "gst_collected": float(data.get("tax1", 0)),
            "qst_collected": float(data.get("tax2", 0)),
            "tips": float(data.get("tips", 0)),
            "voids": float(data.get("voids", 0)),
            "refunds": float(data.get("refunds", 0)),
            "transaction_count": int(data.get("transactionCount", 0)),
            "cash_sales": float(data.get("cashSales", 0)),
            "credit_card_sales": float(data.get("creditCardSales", 0)),
        }

    def _parse_sales_range(self, raw: dict) -> list[dict]:
        """Parse multi-day sales response."""
        days = raw.get("data", [])
        if isinstance(days, dict):
            days = [days]
        return [self._parse_daily_sales(d, d.get("date", "")) for d in days]

    def _parse_clockouts(self, raw: dict) -> list[dict]:
        """Parse employee shift data for tip declaration."""
        shifts = raw.get("data", [])
        if isinstance(shifts, dict):
            shifts = [shifts]
        return [
            {
                "employee_id": s.get("employeeId"),
                "name": s.get("employeeName"),
                "clock_out": s.get("clockOut"),
                "shift_sales": float(s.get("sales", 0)),
                "cc_tips": float(s.get("creditCardTips", 0)),
            }
            for s in shifts
        ]


def get_client() -> LightspeedClient:
    """Create a Lightspeed client."""
    return LightspeedClient()


if __name__ == "__main__":
    if not config.LIGHTSPEED_API_KEY:
        print("Lightspeed Client — NOT READY")
        print("Missing: LIGHTSPEED_API_KEY")
        print("\nTo set up:")
        print("1. Log into Lightspeed Restaurant back-office")
        print("2. Go to Settings → API Access")
        print("3. Generate an API key")
        print("4. Set LIGHTSPEED_API_KEY environment variable")
    else:
        print("Lightspeed Client — credentials found, ready to connect.")
