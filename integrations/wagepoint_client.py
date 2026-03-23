"""
Wagepoint Payroll API Client

Pulls payroll summaries, employee deduction details, and tip data
for reconciliation and PME-6.1 credit calculation.

Requires: WAGEPOINT_API_KEY, WAGEPOINT_COMPANY_ID
Get from: Wagepoint admin panel → Integrations
"""

import json
import urllib.request
import urllib.parse

try:
    from . import config_template as config
except ImportError:
    import config_template as config


class WagepointClient:
    """Wagepoint Payroll API client."""

    def __init__(self):
        self.api_key = config.WAGEPOINT_API_KEY
        self.company_id = config.WAGEPOINT_COMPANY_ID
        self.base_url = f"{config.WAGEPOINT_BASE_URL}/companies/{self.company_id}"

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

    def get_pay_period_summary(self, period_id: str) -> dict:
        """Pull summary for a specific pay period.

        Returns: {
            "period_start": "2025-01-01",
            "period_end": "2025-01-15",
            "total_gross": 12450.00,
            "total_net": 9120.00,
            "total_tips": 5010.00,
            "employer_cpp_qpp": 485.00,
            "employer_ei": 215.00,
            "employer_qpip": 86.00,
            "employees": [...],
        }
        """
        return self._api_get(f"payrolls/{period_id}")

    def get_payrolls_by_date(self, start_date: str, end_date: str) -> list[dict]:
        """Pull all payrolls within a date range."""
        result = self._api_get("payrolls", {
            "start_date": start_date,
            "end_date": end_date,
        })
        return result.get("data", result.get("payrolls", []))

    def get_employee_details(self, employee_id: str) -> dict:
        """Pull employee details including wage rate and position."""
        return self._api_get(f"employees/{employee_id}")

    def get_employees(self) -> list[dict]:
        """Pull all active employees."""
        result = self._api_get("employees", {"status": "active"})
        employees = result.get("data", result.get("employees", []))
        return [
            {
                "id": e.get("id"),
                "name": f"{e.get('first_name', '')} {e.get('last_name', '')}",
                "position": e.get("title", e.get("position", "")),
                "wage_rate": float(e.get("rate", 0)),
                "is_tipped": e.get("receives_tips", False),
            }
            for e in employees
        ]

    def get_tip_summary(self, start_date: str, end_date: str) -> dict:
        """Pull tip totals per employee for PME-6.1 calculation.

        Returns: {
            "period": "2025-01-01_to_2025-01-31",
            "employees": [
                {
                    "id": "E004",
                    "name": "Server A",
                    "declared_tips": 2450.00,
                    "attributed_tips": 0.00,
                    "total_tips": 2450.00,
                    "employer_cpp_on_tips": 156.80,
                    "employer_ei_on_tips": 28.91,
                    "employer_qpip_on_tips": 16.95,
                    "total_employer_premiums_on_tips": 202.66,
                },
            ],
            "total_tips": 5010.00,
            "total_employer_premiums": 677.45,
            "pme_6_1_credit_75pct": 508.09,
        }
        """
        payrolls = self.get_payrolls_by_date(start_date, end_date)

        # Aggregate tips per employee across pay periods
        employee_tips = {}
        for payroll in payrolls:
            for emp in payroll.get("employees", []):
                emp_id = emp.get("id")
                if emp_id not in employee_tips:
                    employee_tips[emp_id] = {
                        "id": emp_id,
                        "name": emp.get("name", ""),
                        "declared_tips": 0.0,
                        "attributed_tips": 0.0,
                        "employer_cpp_on_tips": 0.0,
                        "employer_ei_on_tips": 0.0,
                        "employer_qpip_on_tips": 0.0,
                    }
                t = employee_tips[emp_id]
                t["declared_tips"] += float(emp.get("tips", 0))
                t["attributed_tips"] += float(emp.get("attributed_tips", 0))
                t["employer_cpp_on_tips"] += float(emp.get("employer_cpp_on_tips",
                                                            emp.get("employer_qpp_on_tips", 0)))
                t["employer_ei_on_tips"] += float(emp.get("employer_ei_on_tips", 0))
                t["employer_qpip_on_tips"] += float(emp.get("employer_qpip_on_tips", 0))

        # Calculate totals
        employees = list(employee_tips.values())
        for emp in employees:
            emp["total_tips"] = emp["declared_tips"] + emp["attributed_tips"]
            emp["total_employer_premiums_on_tips"] = (
                emp["employer_cpp_on_tips"] +
                emp["employer_ei_on_tips"] +
                emp["employer_qpip_on_tips"]
            )

        total_tips = sum(e["total_tips"] for e in employees)
        total_premiums = sum(e["total_employer_premiums_on_tips"] for e in employees)

        return {
            "period": f"{start_date}_to_{end_date}",
            "employees": employees,
            "total_tips": total_tips,
            "total_employer_premiums": total_premiums,
            "pme_6_1_credit_75pct": total_premiums * 0.75,
        }

    def get_remittance_status(self, period: str) -> dict:
        """Check if source deductions have been remitted for a period."""
        result = self._api_get("remittances", {"period": period})
        remittances = result.get("data", [])

        return {
            "cra_remitted": any(r.get("authority") == "CRA" and r.get("status") == "remitted"
                                for r in remittances),
            "rq_remitted": any(r.get("authority") == "RQ" and r.get("status") == "remitted"
                               for r in remittances),
            "details": remittances,
        }


def get_client() -> WagepointClient:
    """Create a Wagepoint client."""
    return WagepointClient()


if __name__ == "__main__":
    if not config.WAGEPOINT_API_KEY:
        print("Wagepoint Client — NOT READY")
        print("Missing: WAGEPOINT_API_KEY, WAGEPOINT_COMPANY_ID")
        print("\nTo set up:")
        print("1. Log into Wagepoint admin panel")
        print("2. Go to Settings → Integrations → API")
        print("3. Generate API key")
        print("4. Set environment variables")
    else:
        print("Wagepoint Client — credentials found, ready to connect.")
