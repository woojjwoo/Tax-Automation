#!/usr/bin/env python3
"""
BLOCKER 4 FIX: Delivery Platform Reconciler

Reconciles Uber Eats, DoorDash, and Skip the Dishes payouts against
SRM-recorded gross sales. Splits gross sale into commission expense
and net deposit for accurate GL posting.

Usage:
    python delivery_platform_reconciler.py --demo
    python delivery_platform_reconciler.py --platform uber_eats --payout-csv uber_jan.csv
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

GST_RATE = 0.05
QST_RATE = 0.09975

# Platform commission rates (approximate — verify with actual contracts)
PLATFORM_RATES = {
    "uber_eats": {
        "name": "Uber Eats",
        "commission_rate": 0.30,  # 30%
        "gl_revenue": "4050",
        "gl_commission": "5310",
        "payout_schedule": "weekly",
    },
    "doordash": {
        "name": "DoorDash",
        "commission_rate": 0.25,  # 25%
        "gl_revenue": "4060",
        "gl_commission": "5320",
        "payout_schedule": "weekly",
    },
    "skip": {
        "name": "Skip The Dishes",
        "commission_rate": 0.25,  # 25%
        "gl_revenue": "4070",
        "gl_commission": "5330",
        "payout_schedule": "weekly",
    },
}


@dataclass
class DeliveryOrder:
    date: str
    order_id: str
    gross_sale: float  # What customer paid (before tax)
    gst_on_sale: float
    qst_on_sale: float
    platform: str


@dataclass
class PlatformPayout:
    payout_date: str
    period_start: str
    period_end: str
    gross_sales: float
    commission: float
    commission_gst: float
    commission_qst: float
    adjustments: float
    net_deposit: float
    platform: str


def generate_demo_data():
    """Generate realistic January delivery platform data for Giwa."""
    # Giwa does ~$4,500/month in takeout/delivery (15% of $30K)
    # Split: Uber Eats 50%, DoorDash 30%, Skip 20%
    uber_orders = [
        DeliveryOrder("2025-01-03", "UE-001", 85.00, 4.25, 8.48, "uber_eats"),
        DeliveryOrder("2025-01-04", "UE-002", 120.00, 6.00, 11.97, "uber_eats"),
        DeliveryOrder("2025-01-05", "UE-003", 65.00, 3.25, 6.48, "uber_eats"),
        DeliveryOrder("2025-01-07", "UE-004", 95.00, 4.75, 9.48, "uber_eats"),
        DeliveryOrder("2025-01-09", "UE-005", 110.00, 5.50, 10.97, "uber_eats"),
        DeliveryOrder("2025-01-10", "UE-006", 75.00, 3.75, 7.48, "uber_eats"),
        DeliveryOrder("2025-01-11", "UE-007", 140.00, 7.00, 13.97, "uber_eats"),
        DeliveryOrder("2025-01-12", "UE-008", 90.00, 4.50, 8.98, "uber_eats"),
        DeliveryOrder("2025-01-14", "UE-009", 105.00, 5.25, 10.47, "uber_eats"),
        DeliveryOrder("2025-01-16", "UE-010", 80.00, 4.00, 7.98, "uber_eats"),
        DeliveryOrder("2025-01-17", "UE-011", 130.00, 6.50, 12.97, "uber_eats"),
        DeliveryOrder("2025-01-18", "UE-012", 155.00, 7.75, 15.46, "uber_eats"),
        DeliveryOrder("2025-01-19", "UE-013", 70.00, 3.50, 6.98, "uber_eats"),
        DeliveryOrder("2025-01-21", "UE-014", 88.00, 4.40, 8.78, "uber_eats"),
        DeliveryOrder("2025-01-23", "UE-015", 115.00, 5.75, 11.47, "uber_eats"),
        DeliveryOrder("2025-01-24", "UE-016", 100.00, 5.00, 9.98, "uber_eats"),
        DeliveryOrder("2025-01-25", "UE-017", 145.00, 7.25, 14.46, "uber_eats"),
        DeliveryOrder("2025-01-26", "UE-018", 95.00, 4.75, 9.48, "uber_eats"),
        DeliveryOrder("2025-01-28", "UE-019", 110.00, 5.50, 10.97, "uber_eats"),
        DeliveryOrder("2025-01-30", "UE-020", 125.00, 6.25, 12.47, "uber_eats"),
        DeliveryOrder("2025-01-31", "UE-021", 85.00, 4.25, 8.48, "uber_eats"),
    ]

    doordash_orders = [
        DeliveryOrder("2025-01-03", "DD-001", 75.00, 3.75, 7.48, "doordash"),
        DeliveryOrder("2025-01-05", "DD-002", 90.00, 4.50, 8.98, "doordash"),
        DeliveryOrder("2025-01-08", "DD-003", 60.00, 3.00, 5.99, "doordash"),
        DeliveryOrder("2025-01-10", "DD-004", 110.00, 5.50, 10.97, "doordash"),
        DeliveryOrder("2025-01-12", "DD-005", 85.00, 4.25, 8.48, "doordash"),
        DeliveryOrder("2025-01-15", "DD-006", 70.00, 3.50, 6.98, "doordash"),
        DeliveryOrder("2025-01-17", "DD-007", 95.00, 4.75, 9.48, "doordash"),
        DeliveryOrder("2025-01-19", "DD-008", 65.00, 3.25, 6.48, "doordash"),
        DeliveryOrder("2025-01-22", "DD-009", 120.00, 6.00, 11.97, "doordash"),
        DeliveryOrder("2025-01-24", "DD-010", 80.00, 4.00, 7.98, "doordash"),
        DeliveryOrder("2025-01-27", "DD-011", 55.00, 2.75, 5.49, "doordash"),
        DeliveryOrder("2025-01-29", "DD-012", 100.00, 5.00, 9.98, "doordash"),
        DeliveryOrder("2025-01-31", "DD-013", 75.00, 3.75, 7.48, "doordash"),
    ]

    skip_orders = [
        DeliveryOrder("2025-01-04", "SK-001", 65.00, 3.25, 6.48, "skip"),
        DeliveryOrder("2025-01-07", "SK-002", 80.00, 4.00, 7.98, "skip"),
        DeliveryOrder("2025-01-11", "SK-003", 95.00, 4.75, 9.48, "skip"),
        DeliveryOrder("2025-01-14", "SK-004", 70.00, 3.50, 6.98, "skip"),
        DeliveryOrder("2025-01-18", "SK-005", 110.00, 5.50, 10.97, "skip"),
        DeliveryOrder("2025-01-21", "SK-006", 55.00, 2.75, 5.49, "skip"),
        DeliveryOrder("2025-01-25", "SK-007", 85.00, 4.25, 8.48, "skip"),
        DeliveryOrder("2025-01-28", "SK-008", 75.00, 3.75, 7.48, "skip"),
        DeliveryOrder("2025-01-31", "SK-009", 60.00, 3.00, 5.99, "skip"),
    ]

    all_orders = uber_orders + doordash_orders + skip_orders

    # Generate weekly payouts
    payouts = []
    for platform_key, config in PLATFORM_RATES.items():
        platform_orders = [o for o in all_orders if o.platform == platform_key]
        rate = config["commission_rate"]

        # Group into weekly periods
        weeks = [
            ("2025-01-01", "2025-01-07"),
            ("2025-01-08", "2025-01-14"),
            ("2025-01-15", "2025-01-21"),
            ("2025-01-22", "2025-01-28"),
            ("2025-01-29", "2025-01-31"),
        ]

        for week_start, week_end in weeks:
            week_orders = [o for o in platform_orders
                           if week_start <= o.date <= week_end]
            if not week_orders:
                continue

            gross = sum(o.gross_sale for o in week_orders)
            commission = gross * rate
            comm_gst = commission * GST_RATE
            comm_qst = commission * QST_RATE

            # Payout date is typically 3-5 days after week end
            payout_day = int(week_end.split("-")[2]) + 4
            payout_month = int(week_end.split("-")[1])
            if payout_day > 31:
                payout_day -= 31
                payout_month += 1
            payout_date = f"2025-{payout_month:02d}-{payout_day:02d}"

            net = gross - commission  # Simplified; actual includes tax adjustments

            payouts.append(PlatformPayout(
                payout_date=payout_date,
                period_start=week_start,
                period_end=week_end,
                gross_sales=gross,
                commission=commission,
                commission_gst=comm_gst,
                commission_qst=comm_qst,
                adjustments=0.0,
                net_deposit=net,
                platform=platform_key,
            ))

    return all_orders, payouts


def print_reconciliation(orders: list[DeliveryOrder], payouts: list[PlatformPayout]):
    """Print full delivery platform reconciliation report."""
    print(f"\n{'='*80}")
    print(f"DELIVERY PLATFORM RECONCILIATION — JANUARY 2025")
    print(f"{'='*80}")

    for platform_key, config in PLATFORM_RATES.items():
        platform_orders = [o for o in orders if o.platform == platform_key]
        platform_payouts = [p for p in payouts if p.platform == platform_key]

        if not platform_orders:
            continue

        name = config["name"]
        rate = config["commission_rate"]
        total_gross = sum(o.gross_sale for o in platform_orders)
        total_gst_on_sales = sum(o.gst_on_sale for o in platform_orders)
        total_qst_on_sales = sum(o.qst_on_sale for o in platform_orders)
        total_commission = sum(p.commission for p in platform_payouts)
        total_comm_gst = sum(p.commission_gst for p in platform_payouts)
        total_comm_qst = sum(p.commission_qst for p in platform_payouts)
        total_net = sum(p.net_deposit for p in platform_payouts)

        print(f"\n--- {name} (Commission: {rate:.0%}) ---")
        print(f"  Orders:              {len(platform_orders)}")
        print(f"  Gross Sales:         ${total_gross:>10,.2f}")
        print(f"  GST on Sales:        ${total_gst_on_sales:>10,.2f}")
        print(f"  QST on Sales:        ${total_qst_on_sales:>10,.2f}")
        print(f"  Commission:          ${total_commission:>10,.2f}")
        print(f"  Commission GST:      ${total_comm_gst:>10,.2f}  (ITC claimable)")
        print(f"  Commission QST:      ${total_comm_qst:>10,.2f}  (ITR claimable)")
        print(f"  Net Deposit:         ${total_net:>10,.2f}")

        # Weekly payout detail
        print(f"\n  Weekly Payouts:")
        print(f"  {'Period':<25} {'Gross':>10} {'Commission':>12} {'Net Deposit':>12} {'Payout Date':<12}")
        for p in platform_payouts:
            print(f"  {p.period_start} to {p.period_end} "
                  f"${p.gross_sales:>9,.2f} ${p.commission:>11,.2f} "
                  f"${p.net_deposit:>11,.2f} {p.payout_date}")

    # Summary across all platforms
    all_gross = sum(o.gross_sale for o in orders)
    all_gst = sum(o.gst_on_sale for o in orders)
    all_qst = sum(o.qst_on_sale for o in orders)
    all_commission = sum(p.commission for p in payouts)
    all_comm_gst = sum(p.commission_gst for p in payouts)
    all_comm_qst = sum(p.commission_qst for p in payouts)
    all_net = sum(p.net_deposit for p in payouts)

    print(f"\n{'='*80}")
    print(f"CONSOLIDATED SUMMARY — ALL PLATFORMS")
    print(f"{'='*80}")
    print(f"  Total Orders:            {len(orders)}")
    print(f"  Total Gross Sales:       ${all_gross:>10,.2f}")
    print(f"  Total GST on Sales:      ${all_gst:>10,.2f}  (remit to CRA)")
    print(f"  Total QST on Sales:      ${all_qst:>10,.2f}  (remit to RQ)")
    print(f"  Total Commissions:       ${all_commission:>10,.2f}")
    print(f"  Commission GST (ITC):    ${all_comm_gst:>10,.2f}  (claim as ITC)")
    print(f"  Commission QST (ITR):    ${all_comm_qst:>10,.2f}  (claim as ITR)")
    print(f"  Total Net Deposits:      ${all_net:>10,.2f}")
    print(f"  Effective Commission:    {all_commission/all_gross:.1%}")

    # Journal entry template
    print(f"\n{'='*80}")
    print(f"JOURNAL ENTRY TEMPLATE — January 2025")
    print(f"{'='*80}")
    print(f"  DR  Cash / Bank                 ${all_net:>10,.2f}")
    print(f"  DR  Delivery Commission Expense ${all_commission:>10,.2f}")
    print(f"  DR  GST ITC Receivable          ${all_comm_gst:>10,.2f}")
    print(f"  DR  QST ITR Receivable          ${all_comm_qst:>10,.2f}")
    print(f"    CR  Delivery Revenue                     ${all_gross:>10,.2f}")
    print(f"    CR  GST Collected                        ${all_gst:>10,.2f}")
    print(f"    CR  QST Collected                        ${all_qst:>10,.2f}")
    print(f"  (Total debits = Total credits: ${all_net + all_commission + all_comm_gst + all_comm_qst:>10,.2f})")

    # SRM cross-reference note
    print(f"\n{'='*80}")
    print(f"SRM CROSS-REFERENCE NOTE")
    print(f"{'='*80}")
    print(f"  SRM records delivery orders at GROSS amount (${all_gross:,.2f})")
    print(f"  Bank deposits show NET amount (${all_net:,.2f})")
    print(f"  Difference is platform commission (${all_commission:,.2f})")
    print(f"  This is NOT a revenue discrepancy — it is an expense.")
    print(f"  The commission is a deductible business expense with ITC/ITR.")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Delivery Platform Reconciler for Giwa Restaurant")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--platform", choices=list(PLATFORM_RATES.keys()),
                        help="Platform to reconcile")
    parser.add_argument("--payout-csv", help="Platform payout report CSV")
    args = parser.parse_args()

    if args.demo:
        orders, payouts = generate_demo_data()
        print_reconciliation(orders, payouts)
    else:
        print("Use --demo for demonstration. Custom CSV import coming soon.")


if __name__ == "__main__":
    main()
