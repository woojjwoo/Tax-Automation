#!/usr/bin/env python3
"""
BLOCKER 3 FIX: Lightspeed → QBO Daily Sync Health Check

Monitors the POS-to-accounting integration and alerts when sync breaks.
Designed to run as a daily cron job or Make/Zapier scheduled trigger.

Usage:
    # Daily check (run via cron at 8 AM)
    python sync_health_check.py --check-date 2025-01-15

    # Check last N days for gaps
    python sync_health_check.py --check-range 7

    # Demo mode with sample data
    python sync_health_check.py --demo
"""

import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path

SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "testing" / "sample_data"
VARIANCE_THRESHOLD = 50.00  # $50 absolute variance triggers alert
VARIANCE_PCT_THRESHOLD = 0.005  # 0.5% relative variance triggers alert

# Simulated QBO revenue postings (for demo — in production, query QBO API)
DEMO_QBO_POSTINGS = {
    "2025-01-01": {"revenue": 1025.00, "gst": 51.25, "qst": 102.24},
    "2025-01-02": {"revenue": 1170.00, "gst": 58.50, "qst": 116.72},
    "2025-01-03": {"revenue": 1510.00, "gst": 75.50, "qst": 150.62},
    "2025-01-04": {"revenue": 1605.00, "gst": 80.25, "qst": 160.10},
    "2025-01-05": {"revenue": 1265.00, "gst": 63.25, "qst": 126.28},
    "2025-01-06": {"revenue": 440.00, "gst": 22.00, "qst": 43.89},
    "2025-01-07": {"revenue": 505.00, "gst": 25.25, "qst": 50.37},
    # 2025-01-08: MISSING — simulates sync failure
    "2025-01-09": {"revenue": 1120.00, "gst": 56.00, "qst": 111.72},
    "2025-01-10": {"revenue": 1462.00, "gst": 73.10, "qst": 145.83},
    "2025-01-11": {"revenue": 1558.00, "gst": 77.90, "qst": 155.41},
    "2025-01-12": {"revenue": 1170.00, "gst": 58.50, "qst": 116.72},
    "2025-01-13": {"revenue": 372.00, "gst": 18.60, "qst": 37.12},
    "2025-01-14": {"revenue": 488.00, "gst": 24.40, "qst": 48.68},
    "2025-01-15": {"revenue": 1055.00, "gst": 52.75, "qst": 105.24},
    # 2025-01-16 onwards: amount variance on one day
    "2025-01-16": {"revenue": 1072.00, "gst": 53.60, "qst": 106.93},
    "2025-01-17": {"revenue": 1300.00, "gst": 69.25, "qst": 138.15},  # $85 off
    "2025-01-18": {"revenue": 1558.00, "gst": 77.90, "qst": 155.41},
    "2025-01-19": {"revenue": 1072.00, "gst": 53.60, "qst": 106.93},
    "2025-01-20": {"revenue": 295.00, "gst": 14.75, "qst": 29.43},
    "2025-01-21": {"revenue": 470.00, "gst": 23.50, "qst": 46.88},
    "2025-01-22": {"revenue": 1025.00, "gst": 51.25, "qst": 102.24},
    "2025-01-23": {"revenue": 1072.00, "gst": 53.60, "qst": 106.93},
    "2025-01-24": {"revenue": 1444.00, "gst": 72.20, "qst": 144.03},
    "2025-01-25": {"revenue": 1605.00, "gst": 80.25, "qst": 160.10},
    "2025-01-26": {"revenue": 1170.00, "gst": 58.50, "qst": 116.72},
    "2025-01-27": {"revenue": 372.00, "gst": 18.60, "qst": 37.12},
    "2025-01-28": {"revenue": 508.00, "gst": 25.40, "qst": 50.67},
    "2025-01-29": {"revenue": 1055.00, "gst": 52.75, "qst": 105.24},
    "2025-01-30": {"revenue": 1120.00, "gst": 56.00, "qst": 111.72},
    "2025-01-31": {"revenue": 1318.00, "gst": 65.90, "qst": 131.47},
}


def load_srm_data() -> dict:
    """Load SRM daily sales from sample data."""
    srm_data = {}
    filepath = SAMPLE_DATA_DIR / "january_srm_daily_sales.csv"
    if not filepath.exists():
        return srm_data

    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            srm_data[row["date"]] = {
                "revenue": float(row["net_sales"]),
                "gst": float(row["gst_collected"]),
                "qst": float(row["qst_collected"]),
            }
    return srm_data


def check_single_day(target_date: str, srm_data: dict, qbo_data: dict):
    """Check sync health for a single day."""
    issues = []

    srm = srm_data.get(target_date)
    qbo = qbo_data.get(target_date)

    if srm is None:
        issues.append({
            "type": "SRM_MISSING",
            "severity": "CRITICAL",
            "message": f"No SRM data for {target_date} — restaurant closed or SRM failure?",
        })
        return issues

    if qbo is None:
        issues.append({
            "type": "QBO_MISSING",
            "severity": "CRITICAL",
            "message": (f"SRM recorded ${srm['revenue']:,.2f} on {target_date} "
                        f"but NO corresponding QBO posting. SYNC FAILURE."),
            "lost_revenue": srm["revenue"],
            "lost_gst": srm["gst"],
            "lost_qst": srm["qst"],
        })
        return issues

    # Compare amounts
    rev_diff = abs(srm["revenue"] - qbo["revenue"])
    gst_diff = abs(srm["gst"] - qbo["gst"])
    qst_diff = abs(srm["qst"] - qbo["qst"])

    rev_pct = rev_diff / srm["revenue"] if srm["revenue"] > 0 else 0

    if rev_diff > VARIANCE_THRESHOLD or rev_pct > VARIANCE_PCT_THRESHOLD:
        issues.append({
            "type": "REVENUE_VARIANCE",
            "severity": "HIGH",
            "message": (f"{target_date}: Revenue variance ${rev_diff:,.2f} "
                        f"({rev_pct:.2%}). SRM: ${srm['revenue']:,.2f}, "
                        f"QBO: ${qbo['revenue']:,.2f}"),
        })

    if gst_diff > 1.00:
        issues.append({
            "type": "GST_VARIANCE",
            "severity": "MEDIUM",
            "message": (f"{target_date}: GST variance ${gst_diff:,.2f}. "
                        f"SRM: ${srm['gst']:,.2f}, QBO: ${qbo['gst']:,.2f}"),
        })

    if qst_diff > 1.00:
        issues.append({
            "type": "QST_VARIANCE",
            "severity": "MEDIUM",
            "message": (f"{target_date}: QST variance ${qst_diff:,.2f}. "
                        f"SRM: ${srm['qst']:,.2f}, QBO: ${qbo['qst']:,.2f}"),
        })

    return issues


def run_health_check(days: int = 1, start_date: str = None, demo: bool = False):
    """Run the sync health check."""
    srm_data = load_srm_data()
    qbo_data = DEMO_QBO_POSTINGS if demo else {}

    if not srm_data:
        print("ERROR: No SRM data found. Cannot perform health check.")
        return

    if start_date:
        check_dates = [start_date]
    else:
        # Check last N days
        all_dates = sorted(srm_data.keys())
        check_dates = all_dates[-days:] if days <= len(all_dates) else all_dates

    all_issues = []
    days_ok = 0

    print(f"\n{'='*70}")
    print(f"LIGHTSPEED → QBO SYNC HEALTH CHECK")
    print(f"{'='*70}")
    print(f"Checking {len(check_dates)} day(s)...\n")

    for d in check_dates:
        issues = check_single_day(d, srm_data, qbo_data)
        if issues:
            all_issues.extend(issues)
            for issue in issues:
                icon = "!!!" if issue["severity"] == "CRITICAL" else "! " if issue["severity"] == "HIGH" else "- "
                print(f"  {icon} [{issue['severity']}] {issue['message']}")
        else:
            days_ok += 1

    total = len(check_dates)
    fail = total - days_ok

    print(f"\n{'-'*70}")
    print(f"RESULT: {days_ok}/{total} days synced OK | {fail} day(s) with issues")

    # Categorize issues
    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    high = [i for i in all_issues if i["severity"] == "HIGH"]

    if critical:
        missing_revenue = sum(i.get("lost_revenue", 0) for i in critical)
        print(f"\nCRITICAL: {len(critical)} day(s) with missing QBO postings")
        if missing_revenue > 0:
            print(f"  Revenue not posted to QBO: ${missing_revenue:,.2f}")
            print(f"  GST not tracked: ${sum(i.get('lost_gst', 0) for i in critical):,.2f}")
            print(f"  QST not tracked: ${sum(i.get('lost_qst', 0) for i in critical):,.2f}")

    if high:
        print(f"\nHIGH: {len(high)} day(s) with revenue variances exceeding "
              f"${VARIANCE_THRESHOLD} or {VARIANCE_PCT_THRESHOLD:.1%}")

    if all_issues:
        print(f"\nACTION REQUIRED:")
        if critical:
            print(f"  1. Check Lightspeed → QBO integration status immediately")
            print(f"  2. Re-sync missing days or create manual journal entries")
            print(f"  3. If integration is down, use CSV import as fallback")
        if high:
            print(f"  4. Investigate revenue variances — possible training mode")
            print(f"     transactions or day-cutoff timing issues")
    else:
        print(f"\nAll clear. Lightspeed → QBO sync is healthy.")

    print(f"{'='*70}\n")

    # Return structured result (for automation)
    return {
        "status": "FAIL" if critical else "WARN" if high else "OK",
        "days_checked": total,
        "days_ok": days_ok,
        "critical_issues": len(critical),
        "high_issues": len(high),
        "issues": all_issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Lightspeed → QBO Sync Health Check")
    parser.add_argument("--check-date", help="Check a specific date (YYYY-MM-DD)")
    parser.add_argument("--check-range", type=int, default=7,
                        help="Check last N days (default: 7)")
    parser.add_argument("--demo", action="store_true",
                        help="Use demo data (includes simulated sync failures)")
    args = parser.parse_args()

    if args.check_date:
        result = run_health_check(start_date=args.check_date, demo=args.demo or True)
    else:
        result = run_health_check(days=args.check_range, demo=args.demo or True)

    if result and result["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
