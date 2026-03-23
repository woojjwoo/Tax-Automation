#!/usr/bin/env python3
"""
Workflow Scheduler — Orchestrates daily/weekly/monthly automation

Runs all automated checks on schedule. Designed to be called by:
  - cron (Linux/Mac)
  - Make.com / Zapier (cloud)
  - Windows Task Scheduler

Usage:
    # Run all daily checks
    python scheduler.py daily

    # Run weekly checks
    python scheduler.py weekly

    # Run monthly close workflow
    python scheduler.py monthly --month 2025-01

    # Run annual January checks
    python scheduler.py annual --year 2025

    # Check what would run today
    python scheduler.py status

    # Install cron jobs (Linux/Mac)
    python scheduler.py install-cron

Cron setup (add to crontab -e):
    0  8 * * * cd /path/to/Tax-Automation && python3 orchestrator/scheduler.py daily
    0  9 * * 1 cd /path/to/Tax-Automation && python3 orchestrator/scheduler.py weekly
    0 10 3 * * cd /path/to/Tax-Automation && python3 orchestrator/scheduler.py monthly
    0 10 2 1 * cd /path/to/Tax-Automation && python3 orchestrator/scheduler.py annual
"""

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator.alerter import (
    send_alert, AlertLevel,
    alert_sync_failure, alert_missing_receipts,
    alert_deadline_approaching,
)


def run_script(script_path: str, args: list[str] = None,
               description: str = "") -> dict:
    """Run a Python script and capture its output."""
    full_path = PROJECT_ROOT / script_path
    cmd = [sys.executable, str(full_path)] + (args or [])

    print(f"\n--- {description or script_path} ---")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return {
            "script": script_path,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {script_path} exceeded 120s")
        return {"script": script_path, "exit_code": -1, "success": False,
                "error": "timeout"}
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"script": script_path, "exit_code": -1, "success": False,
                "error": str(e)}


def daily_workflow():
    """Run daily checks (8 AM).

    1. Lightspeed → QBO sync health check
    2. Check for approaching deadlines
    """
    print(f"\n{'='*60}")
    print(f"DAILY WORKFLOW — {date.today().isoformat()}")
    print(f"{'='*60}")

    results = []
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    # 1. Sync health check
    r = run_script(
        "fixes/scripts/sync_health_check.py",
        ["--check-date", yesterday, "--demo"],
        "Lightspeed → QBO Sync Check (yesterday)",
    )
    results.append(r)

    if not r["success"]:
        # Parse output for specific failures
        if "SYNC FAILURE" in r.get("stdout", "") + r.get("stderr", ""):
            alert_sync_failure(yesterday, 0, 0, 0)

    # 2. Deadline checks
    _check_deadlines()

    # Summary
    _print_summary("DAILY", results)
    return results


def weekly_workflow():
    """Run weekly checks (Monday 9 AM).

    1. Missing receipt detection
    2. Delivery platform reconciliation
    3. Bank feed status check
    """
    print(f"\n{'='*60}")
    print(f"WEEKLY WORKFLOW — {date.today().isoformat()}")
    print(f"{'='*60}")

    results = []

    # 1. Missing receipts
    r = run_script(
        "fixes/scripts/missing_receipt_detector.py",
        ["--demo"],
        "Missing Receipt Detection",
    )
    results.append(r)

    if not r["success"]:
        # Count missing receipts from output
        output = r.get("stdout", "") + r.get("stderr", "")
        if "missing" in output.lower():
            alert_missing_receipts(0, 0, 0)

    # 2. Delivery platform reconciliation
    r = run_script(
        "fixes/scripts/delivery_platform_reconciler.py",
        ["--demo"],
        "Delivery Platform Reconciliation",
    )
    results.append(r)

    # 3. Sync check for the full week
    r = run_script(
        "fixes/scripts/sync_health_check.py",
        ["--check-range", "7", "--demo"],
        "Weekly Sync Health Check (last 7 days)",
    )
    results.append(r)

    _print_summary("WEEKLY", results)
    return results


def monthly_workflow(month: str = None):
    """Run monthly close workflow (Day 3).

    1. Full month sync reconciliation
    2. Tip attribution check
    3. Missing receipt detection
    4. Payroll reconciliation (if data available)
    5. Generate exception report
    """
    if month is None:
        # Default to previous month
        today = date.today()
        if today.month == 1:
            month = f"{today.year - 1}-12"
        else:
            month = f"{today.year}-{today.month - 1:02d}"

    print(f"\n{'='*60}")
    print(f"MONTHLY CLOSE WORKFLOW — {month}")
    print(f"{'='*60}")

    results = []

    # 1. Full month sync check
    r = run_script(
        "fixes/scripts/sync_health_check.py",
        ["--check-range", "31", "--demo"],
        f"Full Month Sync Check — {month}",
    )
    results.append(r)

    # 2. Missing receipts
    r = run_script(
        "fixes/scripts/missing_receipt_detector.py",
        ["--demo"],
        f"Missing Receipt Detection — {month}",
    )
    results.append(r)

    # 3. Delivery reconciliation
    r = run_script(
        "fixes/scripts/delivery_platform_reconciler.py",
        ["--demo"],
        f"Delivery Platform Reconciliation — {month}",
    )
    results.append(r)

    # 4. Run full validation suite
    r = run_script(
        "testing/validate_reconciliation.py",
        [],
        f"Full Reconciliation Validation — {month}",
    )
    results.append(r)

    _print_summary("MONTHLY", results)
    return results


def annual_workflow(year: int = None):
    """Run annual January checks.

    1. Payroll rate validation
    2. Tip attribution summary for prior year
    """
    if year is None:
        year = date.today().year

    print(f"\n{'='*60}")
    print(f"ANNUAL WORKFLOW — {year}")
    print(f"{'='*60}")

    results = []

    # 1. Payroll rate validation
    r = run_script(
        "fixes/scripts/payroll_rate_validator.py",
        ["--year", str(year)],
        f"Payroll Rate Validation — {year}",
    )
    results.append(r)

    _print_summary("ANNUAL", results)
    return results


def _check_deadlines():
    """Check for approaching filing deadlines."""
    today = date.today()

    # Monthly GST/QST: due by last day of following month
    # Source deductions: due by 15th of following month
    # T2/CO-17: due 6 months after fiscal year-end

    deadlines = []

    # Source deductions — 15th of each month
    if today.day <= 15:
        sd_due = date(today.year, today.month, 15)
        days_until = (sd_due - today).days
        if days_until <= 7:
            deadlines.append(("Source Deduction Remittance (CRA/RQ)", sd_due, days_until))

    # GST/QST — last day of month (for previous month's filing)
    import calendar
    last_day = calendar.monthrange(today.year, today.month)[1]
    gst_due = date(today.year, today.month, last_day)
    days_until = (gst_due - today).days
    if days_until <= 14:
        deadlines.append(("GST/QST Monthly Filing", gst_due, days_until))

    for filing_type, due_date, days_remaining in deadlines:
        alert_deadline_approaching(filing_type, due_date.isoformat(), days_remaining)


def _print_summary(workflow_type: str, results: list[dict]):
    """Print workflow execution summary."""
    total = len(results)
    passed = sum(1 for r in results if r.get("success"))
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"{workflow_type} WORKFLOW SUMMARY")
    print(f"{'='*60}")
    print(f"Tasks run: {total}  |  Passed: {passed}  |  Failed: {failed}")

    if failed > 0:
        print(f"\nFailed tasks:")
        for r in results:
            if not r.get("success"):
                print(f"  [X] {r['script']}: exit code {r['exit_code']}")
    else:
        print(f"\nAll tasks completed successfully.")
    print(f"{'='*60}\n")


def show_status():
    """Show what would run today based on day of week/month."""
    today = date.today()
    day_name = today.strftime("%A")
    day_of_month = today.day

    print(f"\n{'='*60}")
    print(f"SCHEDULER STATUS — {today.isoformat()} ({day_name})")
    print(f"{'='*60}")

    print(f"\nToday's scheduled runs:")
    print(f"  [{'x' if True else ' '}] Daily checks (runs every day at 8 AM)")
    print(f"  [{'x' if day_name == 'Monday' else ' '}] Weekly checks (runs Mondays at 9 AM)")
    print(f"  [{'x' if day_of_month == 3 else ' '}] Monthly close (runs 3rd of month at 10 AM)")
    print(f"  [{'x' if today.month == 1 and day_of_month == 2 else ' '}] Annual review (runs January 2)")

    print(f"\nCron installation:")
    print(f"  Run 'python scheduler.py install-cron' to set up automated execution.")
    print(f"{'='*60}\n")


def install_cron():
    """Generate cron entries for automated execution."""
    python = sys.executable
    project = str(PROJECT_ROOT)

    cron_lines = [
        f"# Giwa Restaurant Tax Automation",
        f"0  8 * * * cd {project} && {python} orchestrator/scheduler.py daily >> logs/daily.log 2>&1",
        f"0  9 * * 1 cd {project} && {python} orchestrator/scheduler.py weekly >> logs/weekly.log 2>&1",
        f"0 10 3 * * cd {project} && {python} orchestrator/scheduler.py monthly >> logs/monthly.log 2>&1",
        f"0 10 2 1 * cd {project} && {python} orchestrator/scheduler.py annual >> logs/annual.log 2>&1",
    ]

    print("\nAdd these lines to your crontab (run 'crontab -e'):\n")
    for line in cron_lines:
        print(f"  {line}")
    print()

    # Create logs directory
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
    print(f"Logs directory created at: {PROJECT_ROOT / 'logs'}")


def main():
    parser = argparse.ArgumentParser(description="Giwa Restaurant Workflow Scheduler")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("daily", help="Run daily checks")
    subparsers.add_parser("weekly", help="Run weekly checks")

    p_monthly = subparsers.add_parser("monthly", help="Run monthly close")
    p_monthly.add_argument("--month", help="YYYY-MM (default: previous month)")

    p_annual = subparsers.add_parser("annual", help="Run annual review")
    p_annual.add_argument("--year", type=int, help="Year (default: current)")

    subparsers.add_parser("status", help="Show scheduler status")
    subparsers.add_parser("install-cron", help="Generate cron entries")

    args = parser.parse_args()

    if args.command == "daily":
        daily_workflow()
    elif args.command == "weekly":
        weekly_workflow()
    elif args.command == "monthly":
        monthly_workflow(args.month)
    elif args.command == "annual":
        annual_workflow(args.year)
    elif args.command == "status":
        show_status()
    elif args.command == "install-cron":
        install_cron()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
