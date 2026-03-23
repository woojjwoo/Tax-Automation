"""
Uber Eats Merchant API Client

Pulls weekly payout reports and order-level data for delivery
platform reconciliation.

Requires: UBER_EATS_CLIENT_ID, UBER_EATS_CLIENT_SECRET, UBER_EATS_STORE_ID
Get from: Uber Eats Merchant Portal → API tab
"""

import json
import urllib.request
import urllib.parse
from datetime import date, datetime
from pathlib import Path

try:
    from . import config_template as config
except ImportError:
    import config_template as config


class UberEatsClient:
    """Uber Eats Merchant API client."""

    TOKEN_URL = "https://login.uber.com/oauth/v2/token"
    BASE_URL = "https://api.uber.com/v1/eats"

    def __init__(self):
        self.client_id = config.UBER_EATS_CLIENT_ID
        self.client_secret = config.UBER_EATS_CLIENT_SECRET
        self.store_id = config.UBER_EATS_STORE_ID
        self.access_token = None

    def authenticate(self):
        """Get OAuth2 access token (client credentials flow)."""
        data = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "eats.report eats.store.orders.read",
        }).encode()

        req = urllib.request.Request(self.TOKEN_URL, data=data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
        })

        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())

        self.access_token = token_data["access_token"]

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated GET request."""
        if not self.access_token:
            self.authenticate()

        url = f"{self.BASE_URL}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def get_payouts(self, start_date: str, end_date: str) -> list[dict]:
        """Pull payout reports for reconciliation.

        Returns: [
            {
                "payout_date": "2025-01-11",
                "period_start": "2025-01-01",
                "period_end": "2025-01-07",
                "gross_sales": 365.00,
                "commission": 109.50,
                "commission_gst": 5.48,
                "commission_qst": 10.92,
                "adjustments": 0.00,
                "net_deposit": 255.50,
            },
        ]
        """
        result = self._api_get(f"stores/{self.store_id}/payments", {
            "start_date": start_date,
            "end_date": end_date,
        })
        return self._parse_payouts(result)

    def get_orders(self, start_date: str, end_date: str) -> list[dict]:
        """Pull individual orders for detailed reconciliation."""
        result = self._api_get(f"stores/{self.store_id}/orders", {
            "start_date": start_date,
            "end_date": end_date,
        })
        return self._parse_orders(result)

    def _parse_payouts(self, raw: dict) -> list[dict]:
        """Parse payout response."""
        payouts = raw.get("data", raw.get("payments", []))
        parsed = []
        for p in payouts:
            gross = float(p.get("gross_sales", p.get("subtotal", 0)))
            commission = float(p.get("commission", p.get("marketplace_fee", 0)))
            comm_gst = commission * config.GST_RATE
            comm_qst = commission * config.QST_RATE
            net = float(p.get("net_payout", p.get("total", gross - commission)))

            parsed.append({
                "payout_date": p.get("payment_date", p.get("date", "")),
                "period_start": p.get("period_start", ""),
                "period_end": p.get("period_end", ""),
                "gross_sales": gross,
                "commission": commission,
                "commission_gst": comm_gst,
                "commission_qst": comm_qst,
                "adjustments": float(p.get("adjustments", 0)),
                "net_deposit": net,
            })
        return parsed

    def _parse_orders(self, raw: dict) -> list[dict]:
        """Parse orders response."""
        orders = raw.get("data", raw.get("orders", []))
        return [
            {
                "order_id": o.get("id"),
                "date": o.get("placed_at", o.get("date", "")),
                "gross_sale": float(o.get("subtotal", 0)),
                "gst": float(o.get("tax1", 0)),
                "qst": float(o.get("tax2", 0)),
                "status": o.get("status", ""),
            }
            for o in orders
        ]


def get_client() -> UberEatsClient:
    """Create and authenticate an Uber Eats client."""
    client = UberEatsClient()
    client.authenticate()
    return client


if __name__ == "__main__":
    if not config.UBER_EATS_CLIENT_ID:
        print("Uber Eats Client — NOT READY")
        print("Missing: UBER_EATS_CLIENT_ID, UBER_EATS_CLIENT_SECRET, UBER_EATS_STORE_ID")
        print("\nTo set up:")
        print("1. Log into Uber Eats Merchant Portal")
        print("2. Go to API / Integrations section")
        print("3. Generate API credentials")
        print("4. Set environment variables")
    else:
        print("Uber Eats Client — credentials found, ready to connect.")
