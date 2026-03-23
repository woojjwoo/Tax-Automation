"""
QuickBooks Online API Client

Handles OAuth2 token management and all QBO data queries needed
for the reconciliation workflow.

Requires: QBO_CLIENT_ID, QBO_CLIENT_SECRET, QBO_REALM_ID, QBO_REFRESH_TOKEN
Register app at: https://developer.intuit.com/app/developer/qbo/docs/get-started
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


class QBOClient:
    """QuickBooks Online API client with automatic token refresh."""

    TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    BASE_URLS = {
        "sandbox": "https://sandbox-quickbooks.api.intuit.com/v3/company",
        "production": "https://quickbooks.api.intuit.com/v3/company",
    }

    def __init__(self):
        self.client_id = config.QBO_CLIENT_ID
        self.client_secret = config.QBO_CLIENT_SECRET
        self.realm_id = config.QBO_REALM_ID
        self.refresh_token = config.QBO_REFRESH_TOKEN
        self.environment = config.QBO_ENVIRONMENT
        self.access_token = None
        self.base_url = f"{self.BASE_URLS[self.environment]}/{self.realm_id}"
        self._token_file = config.DATA_DIR / ".qbo_tokens.json"

    def _load_cached_token(self):
        """Load cached access token if still valid."""
        if self._token_file.exists():
            data = json.loads(self._token_file.read_text())
            expires = datetime.fromisoformat(data.get("expires_at", "2000-01-01"))
            if datetime.now() < expires:
                self.access_token = data["access_token"]
                self.refresh_token = data.get("refresh_token", self.refresh_token)
                return True
        return False

    def _save_token(self, token_data: dict):
        """Cache token to disk."""
        self._token_file.parent.mkdir(parents=True, exist_ok=True)
        self._token_file.write_text(json.dumps(token_data))

    def authenticate(self):
        """Refresh the OAuth2 access token."""
        if self._load_cached_token():
            return

        if not self.refresh_token:
            raise ValueError(
                "No QBO refresh token. Run the OAuth2 authorization flow first.\n"
                "Visit: https://developer.intuit.com/app/developer/playground"
            )

        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }).encode()

        # Basic auth header
        import base64
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        req = urllib.request.Request(self.TOKEN_URL, data=data, headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())

        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token", self.refresh_token)

        # Cache with expiry
        from datetime import timedelta
        token_data["expires_at"] = (
            datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
        ).isoformat()
        self._save_token(token_data)

    def _api_get(self, endpoint: str, params: dict = None) -> dict:
        """Make an authenticated GET request to QBO API."""
        if not self.access_token:
            self.authenticate()

        url = f"{self.base_url}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _query(self, query_string: str) -> list:
        """Run a QBO SQL-like query."""
        result = self._api_get("query", {"query": query_string})
        return result.get("QueryResponse", {})

    # --- Revenue Queries ---

    def get_revenue_by_date(self, start_date: str, end_date: str) -> dict:
        """Pull daily revenue postings from QBO for a date range.

        Returns: {date_str: {"revenue": float, "gst": float, "qst": float}}
        """
        # Use Profit & Loss report
        result = self._api_get("reports/ProfitAndLoss", {
            "start_date": start_date,
            "end_date": end_date,
            "summarize_column_by": "Days",
            "minorversion": "65",
        })
        return self._parse_pl_report(result)

    def get_sales_tax_summary(self, start_date: str, end_date: str) -> dict:
        """Pull GST/QST collected and ITCs/ITRs for a period."""
        result = self._api_get("reports/TaxSummary", {
            "start_date": start_date,
            "end_date": end_date,
            "minorversion": "65",
        })
        return result

    def get_bank_transactions(self, start_date: str, end_date: str,
                               account_id: str = None) -> list:
        """Pull bank/credit card transactions for matching against Dext."""
        query = (
            f"SELECT * FROM Purchase WHERE TxnDate >= '{start_date}' "
            f"AND TxnDate <= '{end_date}'"
        )
        if account_id:
            query += f" AND AccountRef = '{account_id}'"
        query += " ORDERBY TxnDate"

        result = self._query(query)
        return result.get("Purchase", [])

    def get_payroll_journal_entries(self, start_date: str, end_date: str) -> list:
        """Pull payroll-related journal entries."""
        query = (
            f"SELECT * FROM JournalEntry WHERE TxnDate >= '{start_date}' "
            f"AND TxnDate <= '{end_date}'"
        )
        result = self._query(query)
        return result.get("JournalEntry", [])

    # --- Posting Queries ---

    def post_journal_entry(self, journal_entry: dict) -> dict:
        """Post a journal entry to QBO (e.g., delivery platform reconciliation).

        journal_entry format:
        {
            "TxnDate": "2025-01-31",
            "DocNumber": "DLVR-2025-01",
            "PrivateNote": "Delivery platform reconciliation - January 2025",
            "Line": [
                {"Amount": 2859.35, "DetailType": "JournalEntryLineDetail",
                 "JournalEntryLineDetail": {
                     "PostingType": "Debit",
                     "AccountRef": {"value": "1000", "name": "Cash"},
                 }},
                ...
            ]
        }
        """
        url = f"{self.base_url}/journalentry"
        data = json.dumps(journal_entry).encode()

        req = urllib.request.Request(url, data=data, method="POST", headers={
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def get_bank_feed_status(self) -> list:
        """Check bank feed connection status for all linked accounts."""
        query = "SELECT * FROM Account WHERE AccountType = 'Bank'"
        result = self._query(query)
        accounts = result.get("Account", [])

        statuses = []
        for acct in accounts:
            statuses.append({
                "name": acct.get("Name"),
                "id": acct.get("Id"),
                "balance": acct.get("CurrentBalance"),
                "active": acct.get("Active"),
            })
        return statuses

    # --- Helper Parsers ---

    def _parse_pl_report(self, report: dict) -> dict:
        """Parse P&L report into daily revenue dict."""
        # QBO report format is complex — this extracts the basics
        daily = {}
        columns = report.get("Columns", {}).get("Column", [])
        rows = report.get("Rows", {}).get("Row", [])

        # Extract date headers from columns
        dates = []
        for col in columns:
            meta = col.get("MetaData", [])
            for m in meta:
                if m.get("Name") == "StartDate":
                    dates.append(m.get("Value"))

        # Extract revenue row
        for row in rows:
            header = row.get("Header", {})
            if "Income" in str(header.get("ColData", [{}])[0].get("value", "")):
                cols = row.get("Summary", {}).get("ColData", [])
                for i, col in enumerate(cols):
                    if i < len(dates):
                        daily[dates[i]] = {
                            "revenue": float(col.get("value", 0) or 0)
                        }

        return daily


# --- Convenience functions for scripts ---

def get_client() -> QBOClient:
    """Create and authenticate a QBO client."""
    client = QBOClient()
    client.authenticate()
    return client


if __name__ == "__main__":
    missing = []
    if not config.QBO_CLIENT_ID:
        missing.append("QBO_CLIENT_ID")
    if not config.QBO_CLIENT_SECRET:
        missing.append("QBO_CLIENT_SECRET")
    if not config.QBO_REALM_ID:
        missing.append("QBO_REALM_ID")
    if not config.QBO_REFRESH_TOKEN:
        missing.append("QBO_REFRESH_TOKEN")

    if missing:
        print("QBO Client — NOT READY")
        print(f"Missing: {', '.join(missing)}")
        print("\nTo set up:")
        print("1. Register at https://developer.intuit.com")
        print("2. Create an app (select 'Accounting' scope)")
        print("3. Use OAuth Playground to get initial refresh token")
        print("4. Set environment variables or update config.py")
    else:
        print("QBO Client — credentials found, testing connection...")
        try:
            client = get_client()
            accounts = client.get_bank_feed_status()
            print(f"Connected! Found {len(accounts)} bank account(s).")
            for a in accounts:
                print(f"  - {a['name']}: ${a['balance']:,.2f}")
        except Exception as e:
            print(f"Connection failed: {e}")
