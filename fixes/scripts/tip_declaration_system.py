#!/usr/bin/env python3
"""
BLOCKER 1 FIX: Digital Cash Tip Declaration System

Replaces paper tip forms with a digital workflow that:
- Prompts tipped employees at clock-out to declare cash tips
- Validates against the 8% SRM deemed minimum
- Flags under-declarations for manager review
- Exports tip data to payroll system
- Accumulates data for PME-6.1 credit calculation

Usage:
    # Run as daily clock-out prompt (integrate with POS/time system)
    python tip_declaration_system.py declare --employee E004 --shift-sales 450.00 --cash-tips 55.00

    # Run daily summary
    python tip_declaration_system.py daily-summary --date 2025-01-15

    # Run pay-period export for payroll
    python tip_declaration_system.py payroll-export --period 2025-01-01_to_2025-01-15

    # Run 8% attribution check
    python tip_declaration_system.py attribution-check --period 2025-01-01_to_2025-01-15
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

# --- Configuration ---
TIP_MINIMUM_RATE = 0.08  # 8% deemed minimum (Revenu Québec)
WARNING_RATE = 0.10  # Warn if below 10% (buffer before attribution)
DATA_DIR = Path(__file__).parent.parent / "data" / "tip_declarations"
TIPPED_EMPLOYEES = {
    "E004": {"name": "Server A", "position": "Server"},
    "E005": {"name": "Server B", "position": "Server"},
    "E006": {"name": "Bartender", "position": "Bartender"},
}


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_daily_file(target_date: str) -> Path:
    return DATA_DIR / f"tips_{target_date}.csv"


def declare_tips(employee_id: str, shift_sales: float, cash_tips: float,
                 cc_tips: float = 0.0, target_date: str = None):
    """Record a cash tip declaration for a tipped employee at clock-out."""
    if employee_id not in TIPPED_EMPLOYEES:
        print(f"ERROR: {employee_id} is not a registered tipped employee.")
        print(f"Registered tipped employees: {list(TIPPED_EMPLOYEES.keys())}")
        return False

    if target_date is None:
        target_date = date.today().isoformat()

    total_tips = cash_tips + cc_tips
    tip_rate = total_tips / shift_sales if shift_sales > 0 else 0
    minimum_tips = shift_sales * TIP_MINIMUM_RATE

    # --- Validation ---
    status = "OK"
    warnings = []

    if cash_tips < 0:
        print("ERROR: Cash tips cannot be negative.")
        return False

    if shift_sales <= 0:
        print("ERROR: Shift sales must be positive.")
        return False

    if total_tips < minimum_tips:
        status = "BELOW_MINIMUM"
        shortfall = minimum_tips - total_tips
        warnings.append(
            f"ATTRIBUTION WARNING: Total tips ${total_tips:.2f} are below 8% "
            f"of sales ${shift_sales:.2f}. Minimum: ${minimum_tips:.2f}. "
            f"Shortfall: ${shortfall:.2f} will be attributed."
        )
    elif tip_rate < WARNING_RATE:
        status = "LOW_WARNING"
        warnings.append(
            f"LOW TIP WARNING: Tip rate {tip_rate:.1%} is above 8% but below "
            f"10%. Consider verifying declaration accuracy."
        )

    # --- Record ---
    ensure_data_dir()
    filepath = get_daily_file(target_date)
    file_exists = filepath.exists()

    record = {
        "date": target_date,
        "timestamp": datetime.now().isoformat(),
        "employee_id": employee_id,
        "employee_name": TIPPED_EMPLOYEES[employee_id]["name"],
        "position": TIPPED_EMPLOYEES[employee_id]["position"],
        "shift_sales": f"{shift_sales:.2f}",
        "cc_tips": f"{cc_tips:.2f}",
        "cash_tips": f"{cash_tips:.2f}",
        "total_tips": f"{total_tips:.2f}",
        "tip_rate": f"{tip_rate:.4f}",
        "minimum_required": f"{minimum_tips:.2f}",
        "status": status,
    }

    fieldnames = list(record.keys())
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)

    # --- Output ---
    emp = TIPPED_EMPLOYEES[employee_id]
    print(f"\n{'='*60}")
    print(f"TIP DECLARATION RECORDED")
    print(f"{'='*60}")
    print(f"Employee:     {emp['name']} ({employee_id})")
    print(f"Date:         {target_date}")
    print(f"Shift Sales:  ${shift_sales:,.2f}")
    print(f"CC Tips:      ${cc_tips:,.2f}")
    print(f"Cash Tips:    ${cash_tips:,.2f}")
    print(f"Total Tips:   ${total_tips:,.2f}")
    print(f"Tip Rate:     {tip_rate:.1%}")
    print(f"8% Minimum:   ${minimum_tips:,.2f}")
    print(f"Status:       {status}")

    for w in warnings:
        print(f"\n*** {w}")

    print(f"{'='*60}\n")
    return True


def daily_summary(target_date: str):
    """Print daily tip declaration summary with attribution flags."""
    filepath = get_daily_file(target_date)
    if not filepath.exists():
        print(f"No tip declarations found for {target_date}")
        return

    with open(filepath, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"\n{'='*70}")
    print(f"DAILY TIP SUMMARY — {target_date}")
    print(f"{'='*70}")
    print(f"{'Employee':<15} {'Sales':>10} {'CC Tips':>10} {'Cash Tips':>10} "
          f"{'Total':>10} {'Rate':>8} {'Status':<15}")
    print(f"{'-'*15:<15} {'-'*10:>10} {'-'*10:>10} {'-'*10:>10} "
          f"{'-'*10:>10} {'-'*8:>8} {'-'*15:<15}")

    total_sales = 0
    total_cc = 0
    total_cash = 0
    total_tips = 0
    attribution_count = 0

    for r in rows:
        sales = float(r["shift_sales"])
        cc = float(r["cc_tips"])
        cash = float(r["cash_tips"])
        tips = float(r["total_tips"])
        rate = float(r["tip_rate"])
        status = r["status"]

        total_sales += sales
        total_cc += cc
        total_cash += cash
        total_tips += tips
        if status == "BELOW_MINIMUM":
            attribution_count += 1

        status_display = status
        if status == "BELOW_MINIMUM":
            status_display = "*** ATTRIBUTE"
        elif status == "LOW_WARNING":
            status_display = "! LOW"

        print(f"{r['employee_name']:<15} ${sales:>9,.2f} ${cc:>9,.2f} "
              f"${cash:>9,.2f} ${tips:>9,.2f} {rate:>7.1%} {status_display:<15}")

    overall_rate = total_tips / total_sales if total_sales > 0 else 0
    print(f"{'-'*15:<15} {'-'*10:>10} {'-'*10:>10} {'-'*10:>10} "
          f"{'-'*10:>10} {'-'*8:>8} {'-'*15:<15}")
    print(f"{'TOTAL':<15} ${total_sales:>9,.2f} ${total_cc:>9,.2f} "
          f"${total_cash:>9,.2f} ${total_tips:>9,.2f} {overall_rate:>7.1%}")

    if attribution_count > 0:
        print(f"\n*** {attribution_count} employee(s) require tip attribution "
              f"(below 8% deemed minimum)")
    else:
        print(f"\nAll declarations above 8% minimum. No attribution required.")

    print(f"{'='*70}\n")


def payroll_export(period: str):
    """Export tip data for a pay period in payroll-import format."""
    try:
        start_str, end_str = period.split("_to_")
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)
    except ValueError:
        print(f"ERROR: Invalid period format. Use YYYY-MM-DD_to_YYYY-MM-DD")
        return

    # Aggregate tips per employee across the pay period
    employee_totals = {}
    for emp_id in TIPPED_EMPLOYEES:
        employee_totals[emp_id] = {
            "employee_id": emp_id,
            "employee_name": TIPPED_EMPLOYEES[emp_id]["name"],
            "total_sales": 0.0,
            "total_cc_tips": 0.0,
            "total_cash_tips": 0.0,
            "total_tips": 0.0,
            "shifts_worked": 0,
            "attribution_amount": 0.0,
        }

    current = start
    days_found = 0
    while current <= end:
        filepath = get_daily_file(current.isoformat())
        if filepath.exists():
            days_found += 1
            with open(filepath, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    emp_id = r["employee_id"]
                    if emp_id in employee_totals:
                        t = employee_totals[emp_id]
                        t["total_sales"] += float(r["shift_sales"])
                        t["total_cc_tips"] += float(r["cc_tips"])
                        t["total_cash_tips"] += float(r["cash_tips"])
                        t["total_tips"] += float(r["total_tips"])
                        t["shifts_worked"] += 1
        current = date(current.year, current.month, current.day + 1) if current.day < 28 else \
            date(current.year, current.month + 1, 1) if current.month < 12 else \
            date(current.year + 1, 1, 1)

    # Calculate attributions
    for emp_id, t in employee_totals.items():
        if t["total_sales"] > 0:
            minimum = t["total_sales"] * TIP_MINIMUM_RATE
            if t["total_tips"] < minimum:
                t["attribution_amount"] = minimum - t["total_tips"]

    # Output payroll-ready CSV
    output_file = DATA_DIR / f"payroll_tips_{period}.csv"
    fieldnames = [
        "employee_id", "employee_name", "pay_period",
        "total_sales", "cc_tips", "declared_cash_tips",
        "total_declared_tips", "attribution_amount",
        "total_tips_for_payroll", "shifts_worked",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for emp_id, t in employee_totals.items():
            total_for_payroll = t["total_tips"] + t["attribution_amount"]
            writer.writerow({
                "employee_id": emp_id,
                "employee_name": t["employee_name"],
                "pay_period": period,
                "total_sales": f"{t['total_sales']:.2f}",
                "cc_tips": f"{t['total_cc_tips']:.2f}",
                "declared_cash_tips": f"{t['total_cash_tips']:.2f}",
                "total_declared_tips": f"{t['total_tips']:.2f}",
                "attribution_amount": f"{t['attribution_amount']:.2f}",
                "total_tips_for_payroll": f"{total_for_payroll:.2f}",
                "shifts_worked": t["shifts_worked"],
            })

    print(f"\nPayroll tip export saved to: {output_file}")
    print(f"Period: {period} ({days_found} days with declarations found)")

    # Print summary
    print(f"\n{'Employee':<15} {'Declared':>12} {'Attributed':>12} {'For Payroll':>12}")
    print(f"{'-'*15:<15} {'-'*12:>12} {'-'*12:>12} {'-'*12:>12}")
    for emp_id, t in employee_totals.items():
        total_for_payroll = t["total_tips"] + t["attribution_amount"]
        print(f"{t['employee_name']:<15} "
              f"${t['total_tips']:>11,.2f} "
              f"${t['attribution_amount']:>11,.2f} "
              f"${total_for_payroll:>11,.2f}")
    print()


def attribution_check(period: str):
    """Check if any employee requires tip attribution for the pay period."""
    try:
        start_str, end_str = period.split("_to_")
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)
    except ValueError:
        print(f"ERROR: Invalid period format. Use YYYY-MM-DD_to_YYYY-MM-DD")
        return

    employee_totals = {emp_id: {"sales": 0.0, "tips": 0.0}
                       for emp_id in TIPPED_EMPLOYEES}

    current = start
    while current <= end:
        filepath = get_daily_file(current.isoformat())
        if filepath.exists():
            with open(filepath, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    emp_id = r["employee_id"]
                    if emp_id in employee_totals:
                        employee_totals[emp_id]["sales"] += float(r["shift_sales"])
                        employee_totals[emp_id]["tips"] += float(r["total_tips"])
        try:
            current = date.fromordinal(current.toordinal() + 1)
        except ValueError:
            break

    print(f"\n{'='*70}")
    print(f"TIP ATTRIBUTION CHECK — {period}")
    print(f"{'='*70}")
    print(f"{'Employee':<15} {'Sales':>10} {'Tips':>10} {'Rate':>8} "
          f"{'Min (8%)':>10} {'Shortfall':>10} {'Action':<12}")
    print("-" * 75)

    any_attribution = False
    for emp_id, data in employee_totals.items():
        if data["sales"] == 0:
            continue
        rate = data["tips"] / data["sales"]
        minimum = data["sales"] * TIP_MINIMUM_RATE
        shortfall = max(0, minimum - data["tips"])
        action = "ATTRIBUTE" if shortfall > 0 else "OK"
        if shortfall > 0:
            any_attribution = True

        print(f"{TIPPED_EMPLOYEES[emp_id]['name']:<15} "
              f"${data['sales']:>9,.2f} ${data['tips']:>9,.2f} "
              f"{rate:>7.1%} ${minimum:>9,.2f} "
              f"${shortfall:>9,.2f} {action:<12}")

    print("-" * 75)
    if any_attribution:
        print("ACTION REQUIRED: Attribute shortfall amounts via payroll system.")
        print("Source deductions must be calculated on attributed tips.")
    else:
        print("No attribution required. All employees above 8% minimum.")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Giwa Restaurant Tip Declaration System")
    subparsers = parser.add_subparsers(dest="command")

    # declare
    p_declare = subparsers.add_parser("declare", help="Record a tip declaration")
    p_declare.add_argument("--employee", required=True, help="Employee ID (e.g., E004)")
    p_declare.add_argument("--shift-sales", type=float, required=True)
    p_declare.add_argument("--cash-tips", type=float, required=True)
    p_declare.add_argument("--cc-tips", type=float, default=0.0)
    p_declare.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")

    # daily-summary
    p_daily = subparsers.add_parser("daily-summary", help="Show daily summary")
    p_daily.add_argument("--date", required=True, help="YYYY-MM-DD")

    # payroll-export
    p_payroll = subparsers.add_parser("payroll-export", help="Export tips for payroll")
    p_payroll.add_argument("--period", required=True,
                           help="YYYY-MM-DD_to_YYYY-MM-DD")

    # attribution-check
    p_attr = subparsers.add_parser("attribution-check",
                                   help="Check 8% attribution requirement")
    p_attr.add_argument("--period", required=True,
                        help="YYYY-MM-DD_to_YYYY-MM-DD")

    args = parser.parse_args()

    if args.command == "declare":
        declare_tips(args.employee, args.shift_sales, args.cash_tips,
                     args.cc_tips, args.date)
    elif args.command == "daily-summary":
        daily_summary(args.date)
    elif args.command == "payroll-export":
        payroll_export(args.period)
    elif args.command == "attribution-check":
        attribution_check(args.period)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
